import neat
import pickle
import os
import tempfile
import json
import threading
import pygame
from multiprocessing import cpu_count

from demomunk.main import Game, SpeciesBundle

def build_neat_config(num_inputs, num_outputs):  # wow im so good at coding
    config_text = f"""
[NEAT]
fitness_criterion       = max
fitness_threshold       = 500
pop_size                = 250
reset_on_extinction     = False
no_fitness_termination  = True

[DefaultGenome]
num_inputs              = {num_inputs}
num_outputs             = {num_outputs}
num_hidden              = 0
initial_connection      = full

enabled_default         = False
enabled_mutate_rate     = 0.1
enabled_rate_to_true_add  = 0
enabled_rate_to_false_add = 0

feed_forward            = True
compatibility_disjoint_coefficient = 1
compatibility_weight_coefficient   = 1

activation_default      = random
activation_mutate_rate  = 0.1
activation_options      = tanh sin elu gauss inv sigmoid

aggregation_default     = random
aggregation_mutate_rate = 0.1
aggregation_options     = min max sum product mean

bias_init_type          = gaussian
bias_init_mean          = 0.0
bias_init_stdev         = 1.0
bias_max_value          = 20.0
bias_min_value          = -20.0
bias_mutate_power       = 0.3
bias_mutate_rate        = 0.8
bias_replace_rate       = 0.1

weight_init_mean        = 0.0
weight_init_stdev       = 1.0
weight_init_type        = gaussian
weight_max_value        = 20
weight_min_value        = -20
weight_mutate_power     = 0.5
weight_mutate_rate      = 0.9
weight_replace_rate     = 0.1

conn_add_prob           = 0.6
conn_delete_prob        = 0.25
node_add_prob           = 0.15
node_delete_prob        = 0.15

response_init_mean      = 1.0
response_init_stdev     = 0.0
response_init_type      = gaussian
response_max_value      = 30.0
response_min_value      = -30.0
response_mutate_power   = 0.0
response_mutate_rate    = 0.0
response_replace_rate   = 0.0

single_structural_mutation = false
structural_mutation_surer  = default

[DefaultSpeciesSet]
compatibility_threshold = 4.0

[DefaultStagnation]
species_fitness_func    = max
max_stagnation          = 15
species_elitism         = 1

[DefaultReproduction]
elitism             = 2
survival_threshold  = 0.1
min_species_size    = 1
"""
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cfg")
    tmp.write(config_text)
    tmp.close()
    config = neat.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        tmp.name,
    )
    os.unlink(tmp.name)
    return config, config_text

class GenomeEvaluator:
    def __init__(self, creature_data):
        self.creature_data = creature_data

    def __call__(self, genome, config):
        net            = neat.nn.FeedForwardNetwork.create(genome, config)
        game           = Game(render=False)
        game.creature_json = self.creature_data
        fitness        = game.run_genome(net)
        genome.fitness = fitness
        return fitness

def get_genome_dimensions(creature_data):
    num_bodies  = len(creature_data["bodies"])
    num_springs = sum(1 for j in creature_data["joints"] if j["actuated"])
    return 2 + num_bodies * 3, num_springs

def build_bundles(pop, config, gen, species_appeared, genome_appeared):
    best_sid = max(pop.species.species.items(),key=lambda kv: max((g.fitness or -999999) for g in kv[1].members.values()))[0]

    bundles = []
    for sid, species in sorted(pop.species.species.items()):
        if sid not in species_appeared:
            species_appeared[sid] = gen

        stagnation = gen - species.last_improved

        members = []
        for genome in species.members.values():
            if genome.fitness is not None:
                if genome.key not in genome_appeared:
                    genome_appeared[genome.key] = gen
                    genome.appeared_gen = gen
                net = neat.nn.FeedForwardNetwork.create(genome, config)
                members.append((genome, net, genome.fitness))
        members.sort(key=lambda x: x[2], reverse=True)

        if not members:
            continue

        bundles.append(SpeciesBundle(
            sid = sid,
            name = "",
            members = members,
            stagnation = stagnation,
            is_best = (sid == best_sid),
            appeared_gen = species_appeared[sid],
            gen_number = gen,
        ))

    bundles.sort(key=lambda b: b.avg_fitness, reverse=True)
    return bundles


def run_neat(generations=1000000, num_workers=None, import_path=None, creature_data=None):
    # if importing, extract creature_data from the state file first
    if import_path and creature_data is None:
        import pickle
        with open(import_path, 'rb') as f:
            saved = pickle.load(f)
        if isinstance(saved['creature_json'], dict):
            creature_data = saved['creature_json']
        else:
            creature_data = json.loads(saved['creature_json'])

    num_inputs, num_outputs = get_genome_dimensions(creature_data)
    config, config_text = build_neat_config(num_inputs, num_outputs)
    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())

    num_workers = num_workers or cpu_count()
    print(f"Using {num_workers} parallel workers.")

    evaluator = neat.ParallelEvaluator(num_workers, GenomeEvaluator(creature_data))
    viewer = Game(render=True)
    viewer.config = config
    viewer.creature_json = creature_data
    viewer._neat_config_text = config_text
    

    if import_path:
        viewer.load_state(import_path)
        viewer._viewer_loop()
        # rebuild so we can continue training
        last_bundles = viewer.gen_history[-1]
        all_genomes  = []
        for bundle in last_bundles:
            for genome, net, fitness in bundle.members:
                all_genomes.append(genome)
        pop.population = {g.key: g for g in all_genomes}
        pop.species.speciate(config, pop.population, pop.generation)
    else:
        eval_thread = threading.Thread(target=evaluator.evaluate, args=(list(pop.population.items()), config))
        eval_thread.start()
        eval_thread.join()

    best = None
    species_appeared = {}
    genome_appeared = {}

    for gen in range(generations):
        print(f"\n---- Generation {gen} ----")

        for gid, genome in pop.population.items():
            if gid not in genome_appeared:
                genome_appeared[gid] = gen
                genome.appeared_gen = gen

        bundles = build_bundles(pop, config, gen, species_appeared, genome_appeared)
        best = max(pop.population.values(), key=lambda g: g.fitness or -999999)

        pop.population = pop.reproduction.reproduce(config, pop.species, config.pop_size, pop.generation)
        if not pop.species.species:
            pop.population = pop.reproduction.create_new(config.genome_type, config.genome_config, config.pop_size)
        pop.species.speciate(config, pop.population, pop.generation)
        pop.generation += 1

        eval_thread = threading.Thread(target=evaluator.evaluate, args=(list(pop.population.items()), config))
        eval_thread.start()

        print(f"Rendering {len(bundles)} species.")
        viewer.push_and_show(bundles)

        eval_thread.join()

    with open("best_genome.pkl", "wb") as f:
        pickle.dump(best, f)

    print("\nBest genome:\n", best)


if __name__ == "__main__":
    run_neat()
