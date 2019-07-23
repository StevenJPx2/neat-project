import os
import pickle

import Creature

import neat
from neat.math_util import mean
import visualize 

runs_per_net = 5
simulation_seconds = 60.0
time_const = Creature.EPOCH_DELAY

simulation_field = Creature.Field(30, 30, nibbles = 100)

def eval_genome(genome, config):
    net = neat.ctrnn.CTRNN.create(genome, config, time_const)

    fitnesses = []
    for runs in range(runs_per_net):
        sim = Creature.Creature(simulation_field)
        net.reset()

        # Run the given simulation for up to num_steps time steps.
        fitness = 0.0
        while sim.total_time < simulation_seconds:
            inputs = sim.return_inputs()
            action = net.advance(inputs, time_const, time_const)

            sim.move_AI(action)

            fitness = sim.fitness

        fitnesses.append(fitness)

        #print("{0} fitness {1}".format(net, fitness))


    # The genome's fitness is its worst performance across all runs.
    return min(fitnesses)


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-ctrnn')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    if 0:
        winner = pop.run(eval_genomes)
    else:
        pe = neat.ParallelEvaluator(4, eval_genome)
        winner = pop.run(pe.evaluate)

    # Save the winner.
    with open('winner-ctrnn', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)

    visualize.plot_stats(stats, ylog=True, view=True, filename="ctrnn-fitness.svg")
    visualize.plot_species(stats, view=True, filename="ctrnn-speciation.svg")

    node_names = {-1: 'top left', -2: 'top', -3: 'top right', -4: 'left', 0: 'center', 1: 'right', 2: 'bottom left', 3: 'bottom', 4: 'bottom right'}
    visualize.draw_net(config, winner, True, node_names=node_names)

    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="winner-ctrnn.gv")
    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="winner-ctrnn-enabled.gv", show_disabled=False)
    visualize.draw_net(config, winner, view=True, node_names=node_names,
                       filename="winner-ctrnn-enabled-pruned.gv", show_disabled=False, prune_unused=True)


if __name__ == '__main__':
    run()


