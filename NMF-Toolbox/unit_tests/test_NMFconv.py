"""
    Name: test_NMFconv
    Date of Revision: Jul 2019
    Programmer: Christian Dittmar, Yiğitcan Özer

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    If you use the 'NMF toolbox' please refer to:
    [1] Patricio López-Serrano, Christian Dittmar, Yiğitcan Özer, and Meinard
        Müller
        NMF Toolbox: Music Processing Applications of Nonnegative Matrix
        Factorization
        In Proceedings of the International Conference on Digital Audio Effects
        (DAFx), 2019.

    License:
    This file is part of 'NMF toolbox'.
    https://www.audiolabs-erlangen.de/resources/MIR/NMFtoolbox/
    'NMF toolbox' is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    the Free Software Foundation, either version 3 of the License, or (at
    your option) any later version.

    'NMF toolbox' is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
    Public License for more details.

    You should have received a copy of the GNU General Public License along
    with 'NMF toolbox'. If not, see http://www.gnu.org/licenses/.
"""

import os
import numpy as np
import scipy.io.wavfile as wav

from NMFtoolbox.forwardSTFT import forwardSTFT
from NMFtoolbox.initTemplates import initTemplates
from NMFtoolbox.initActivations import initActivations
from NMFtoolbox.utils import make_monaural, pcmInt16ToFloat32Numpy
from NMFtoolbox.NMFconv import NMFconv


def run_NMFconv():
    inpPath = '../data'
    filename = 'runningExample_AmenBreak.wav'

    # read signals
    fs, x = wav.read(os.path.join(inpPath, filename))

    # make monaural if necessary
    x = make_monaural(x)

    # convert wav from int16 to float32
    x = pcmInt16ToFloat32Numpy(x)

    paramSTFT = dict()
    paramSTFT['blockSize'] = 2048
    paramSTFT['hopSize'] = 512
    paramSTFT['winFunc'] = np.hanning(paramSTFT['blockSize'])
    paramSTFT['reconstMirror'] = True
    paramSTFT['appendFrame'] = True
    paramSTFT['numSamples'] = len(x)

    # STFT computation
    X, A, P = forwardSTFT(x, paramSTFT)

    # get dimensions and time and freq resolutions
    numBins, numFrames = X.shape
    deltaT = paramSTFT['hopSize'] / fs
    deltaF = fs / paramSTFT['blockSize']

    # 3. apply NMF variants to STFT magnitude
    # set common parameters
    numComp = 3
    numIter = 3
    numTemplateFrames = 8

    # generate initial guess for templates
    paramTemplates = dict()
    paramTemplates['deltaF'] = deltaF
    paramTemplates['numComp'] = numComp
    paramTemplates['numBins'] = numBins
    paramTemplates['numTemplateFrames'] = numTemplateFrames
    initW = initTemplates(paramTemplates, 'drums')

    # generate initial activations
    paramActivations = dict()
    paramActivations['numComp'] = numComp
    paramActivations['numFrames'] = numFrames
    initH = initActivations(paramActivations, 'uniform')

    # NMFconv parameters
    paramNMFconv = dict()

    paramNMFconv['numComp'] = numComp
    paramNMFconv['numFrames'] = numFrames
    paramNMFconv['numIter'] = numIter
    paramNMFconv['numTemplateFrames'] = numTemplateFrames
    paramNMFconv['initW'] = initW
    paramNMFconv['initH'] = initH
    paramNMFconv['beta'] = 0

    # NMFconv core method
    nmfconvW, nmfconvH, nmfconvV, divBeta = NMFconv(A, paramNMFconv)

    python_res = {'nmfconvW': nmfconvW,
                  'nmfconvH': nmfconvH,
                  'nmfconvV': nmfconvV,
                  'divBeta': divBeta.reshape(1, -1)}

    return python_res
