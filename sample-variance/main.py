# -*- coding: utf-8 -*-

from __future__ import division

import numpy as np
from random import sample as generate_sample
from random import randint
import multiprocessing

import time

verbose = False
k = 1000        # Amount of tests
N = 1000000     # Amount of members in population
a, b = 1, 1000  # Range of integers
n = 500         # Amount of members in sample


def run_experiment(sums):
    population = []

    for j in range(N):
        integer = randint(a, b)

        population.append(integer)

    # Calculate parameters of population
    population_sigma2 = np.var(population)
    population_sigma = np.std(population)
    sample = generate_sample(population, n)
    sample_sigma2 = np.var(sample)
    sample_sigma = np.std(sample)
    sample_s2 = np.var(sample, ddof=1)
    sample_s = np.std(sample, ddof=1)

    sigma2_minus_s2 = abs(population_sigma2 - sample_s2)
    sigma_minus_s = abs(population_sigma - sample_s)
    sigma2_minus_sigma2 = abs(population_sigma2 - sample_sigma2)
    sigma_minus_sigma = abs(population_sigma - sample_sigma)

    arg = {
        'population': {
            'sigma2': population_sigma2,
            'sigma': population_sigma
        },
        'sample': {
            'sigma2': sample_sigma2,
            'sigma': sample_sigma,
            's2': sample_s2,
            's': sample_s
        },
        'statistics': {
            'sigma2_minus_s2': sigma2_minus_s2,
            'sigma_minus_s': sigma_minus_s,
            'sigma2_minus_sigma2': sigma2_minus_sigma2,
            'sigma_minus_sigma': sigma_minus_sigma
        }
    }

    sums['sigma2_minus_s2'] += arg['statistics']['sigma2_minus_s2']
    sums['sigma_minus_s'] += arg['statistics']['sigma_minus_s']
    sums['sigma2_minus_sigma2'] += arg['statistics']['sigma2_minus_sigma2']
    sums['sigma_minus_sigma'] += arg['statistics']['sigma_minus_sigma']

    if verbose:
        print "Population: σ² = %5.5f, σ = %5.5f" % (arg['population']['sigma2'], arg['population']['sigma'])
        print "Sample:     σ² = %5.5f, σ = %5.5f" % (arg['sample']['sigma2'], arg['sample']['sigma'])
        print "            S² = %5.5f, σ = %5.5f" % (arg['sample']['s2'], arg['sample']['s'])
        print "         σ²-S² = %5.5f, σ²(pop)-σ²(samp)=%5.5f" % (arg['statistics']['sigma2_minus_s2'], arg['statistics']['sigma_minus_s'])
        print "-----"


if __name__ == '__main__':
    cores = multiprocessing.cpu_count()
    manager = multiprocessing.Manager()
    sums = manager.dict()
    sums['sigma2_minus_s2'] = 0
    sums['sigma_minus_s'] = 0
    sums['sigma2_minus_sigma2'] = 0
    sums['sigma_minus_sigma'] = 0

    left = k
    while left > 1:
        diff = cores - len(multiprocessing.active_children()) -1
        if diff > 0:
            for i in range(diff):
                p = multiprocessing.Process(target=run_experiment, args=(sums, ))
                p.start()

            left -= diff
            print "%d tests left" % left

        time.sleep(0.25)

    # Lets wait for processes that are still doing their thing
    while len(multiprocessing.active_children()) > 1:
        time.sleep(1)

    sums['sigma2_minus_s2'] /= k
    sums['sigma_minus_s'] /= k
    sums['sigma2_minus_sigma2'] /= k
    sums['sigma_minus_sigma'] /= k

    print "Averages:"
    print "|σ²-σ²| = %5.5f" % sums['sigma2_minus_sigma2']
    print "|σ²-S²| = %5.5f" % sums['sigma2_minus_s2']
    print "|σ-σ| = %5.5f" % sums['sigma_minus_sigma']
    print "|σ-S| = %5.5f" % sums['sigma_minus_s']