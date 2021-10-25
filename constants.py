#GENE
UPPER_WEIGHT_BOUND  = 10.0
LOWER_WEIGHT_BOUND  = -10.0

WEIGHT_CHANGE_POWER = 1.0#std when choosing a new weight for gene
WEIGHT_ADJUST_POWER = 0.5#std when adjustin current weight
PROB_CHANGE_WEIGHT  = 0.1#probability to choose a new gene

USE_GAUSS           = False#IF TRUE USE GAUSS DIST ELSE UNIFORM DIST

#GENOME
PROB_MUTATE_GENE    = 0.8
PROB_ADD_GENE       = 0.2
PROB_ADD_NODE       = 0.5
DISABLE_AFTER_CROSS = 0.75

CREATE_CON_TRIES = 5
ADD_NODE_TRIES = 5

#SPECIES
CUT_OFF                      = 0.2
WEIGTH_DIFF_COEF             = 0.5
EXCESS_DISJOINT_COEF         = 1.0
LARGE_GENOME_THRES           = 20#Number of genes for a genome to be considered a large genome
PROB_CLONE_MEMBER            = 0.25
MIN_AFTER_CUT_OFF            = 2#Minimum number of genomes to be left after cut off
TRYS_IN_TOURNAMENT_SELECTION = 3
TARGET_SPECIES   = 30
ELITISM = 2

#POPULATION
POP_SIZE         = 50
INPUT_COUNT      = 2
OUTPUT_COUNT     = 1
STAGNATION_LIMIT = 20

ALPHA_LOWER  = 0.95
ALPHA_HIGHER = 1.05

#fitnesses adjustments based on the age
YOUNGE_AGE_FITNESS_BONUSS = 1.3
YOUNGE_AGE_THRESHHOLD     = 10
OLD_AGE_FITNESS_PENALTY   = 0.7
OLD_AGE_THRESHOLD         = 50