"""Implementation of Closed-Form Matting.

This module implements natural image matting method described in:
    Levin, Anat, Dani Lischinski, and Yair Weiss. "A closed-form solution to natural image matting."
    IEEE Transactions on Pattern Analysis and Machine Intelligence 30.2 (2008): 228-242.

"""

from __future__ import division

import logging

import cv2
import numpy as np
from numpy.lib.stride_tricks import as_strided
import scipy.sparse
import scipy.sparse.linalg


def _rolling_block(A, block=(3, 3)):
    """Applies sliding window to given matrix."""
    shape = (A.shape[0] - block[0] + 1, A.shape[1] - block[1] + 1) + block
    strides = (A.strides[0], A.strides[1]) + A.strides
    return as_strided(A, shape=shape, strides=strides)


def compute_laplacian(img, mask=None, eps=10**(-7), win_rad=1):
    """Computes Matting Laplacian for a given image.

    Args:
        img: 3-dim numpy matrix with input image
        mask: mask of pixels for which Laplacian will be computed.
            If not set Laplacian will be computed for all pixels.
        eps: regularization parameter controlling alpha smoothness
            from Eq. 12 of the original paper. Defaults to 1e-7.
        win_rad: radius of window used to build Matting Laplacian (i.e.
            radius of omega_k in Eq. 12).
    Returns: sparse matrix holding Matting Laplacian.
    """

    win_size = (win_rad * 2 + 1) ** 2
    h, w, d = img.shape
    # Number of window centre indices in h, w axes
    c_h, c_w = h - 2 * win_rad, w - 2 * win_rad
    win_diam = win_rad * 2 + 1

    indsM = np.arange(h * w).reshape((h, w))
    ravelImg = img.reshape(h * w, d)
    win_inds = _rolling_block(indsM, block=(win_diam, win_diam))

    win_inds = win_inds.reshape(c_h, c_w, win_size)
    if mask is not None:
        mask = cv2.dilate(
            mask.astype(np.uint8),
            np.ones((win_diam, win_diam), np.uint8)
        ).astype(np.bool)
        win_mask = np.sum(mask.ravel()[win_inds], axis=2)
        win_inds = win_inds[win_mask > 0, :]
    else:
        win_inds = win_inds.reshape(-1, win_size)

    
    winI = ravelImg[win_inds]

    win_mu = np.mean(winI, axis=1, keepdims=True)
    win_var = np.einsum('...ji,...jk ->...ik', winI, winI) / win_size - np.einsum('...ji,...jk ->...ik', win_mu, win_mu)

    inv = np.linalg.inv(win_var + (eps/win_size)*np.eye(3))

    X = np.einsum('...ij,...jk->...ik', winI - win_mu, inv)
    vals = np.eye(win_size) - (1.0/win_size)*(1 + np.einsum('...ij,...kj->...ik', X, winI - win_mu))

    nz_indsCol = np.tile(win_inds, win_size).ravel()
    nz_indsRow = np.repeat(win_inds, win_size).ravel()
    nz_indsVal = vals.ravel()
    L = scipy.sparse.coo_matrix((nz_indsVal, (nz_indsRow, nz_indsCol)), shape=(h*w, h*w))
    return L


def closed_form_matting_with_prior(image, prior, prior_confidence, consts_map=None):
    """Applies closed form matting with prior alpha map to image.

    Args:
        image: 3-dim numpy matrix with input image.
        prior: matrix of same width and height as input image holding apriori alpha map.
        prior_confidence: matrix of the same shape as prior hodling confidence of prior alpha.
        consts_map: binary mask of pixels that aren't expected to change due to high
            prior confidence.

    Returns: 2-dim matrix holding computed alpha map.
    """

    assert image.shape[:2] == prior.shape, ('prior must be 2D matrix with height and width equal '
                                            'to image.')
    assert image.shape[:2] == prior_confidence.shape, ('prior_confidence must be 2D matrix with '
                                                       'height and width equal to image.')
    assert (consts_map is None) or image.shape[:2] == consts_map.shape, (
        'consts_map must be 2D matrix with height and width equal to image.')

    logging.info('Computing Matting Laplacian.')
    laplacian = compute_laplacian(image, ~consts_map if consts_map is not None else None)

    confidence = scipy.sparse.diags(prior_confidence.ravel())
    logging.info('Solving for alpha.')
    solution = scipy.sparse.linalg.spsolve(
        laplacian + confidence,
        prior.ravel() * prior_confidence.ravel()
    )
    alpha = np.minimum(np.maximum(solution.reshape(prior.shape), 0), 1)
    return alpha


def closed_form_matting_with_scribbles(image, scribbles, scribbles_confidence=100.0):
    """Apply Closed-Form matting to given image using scribbles image."""

    assert image.shape == scribbles.shape, 'scribbles must have exactly same shape as image.'
    prior = np.sign(np.sum(scribbles - image, axis=2)) / 2 + 0.5
    consts_map = prior != 0.5
    return closed_form_matting_with_prior(
        image,
        prior,
        scribbles_confidence * consts_map,
        consts_map
    )




if __name__ == "__main__":
    main()
