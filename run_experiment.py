import sys, shutil, os, filecmp                                             # utility imports
import free_strat, prefix, suffix, seed_strat, educate_strat, smgPrefix       # PRISM-generating files

# Reads log.txt and returns last found p(win)
def find_prev_result():
    info = open("log.txt", "r").readlines()
    l = len(info)
    res = ""
    prop = ""
    # find prop & result
    for i in range(1,l):
        if info[l-i][:8] == "Result: " and res == "":
            res = info[l-i][8:20]
        if "Model checking: " in info[l-i] and prop == "":
            prop = info[l-i].split("Model checking: ")[1][:-1]
            break;
    return float(res)

# Takes 4 characters and returns opt(win) for either team as two floats
def optimality(characters):
    # Generate a prism file to represent SMG of game between both teams
    sys.stdout=open("smg.prism","w")
    smgPrefix.run(characters)
    free_strat.run(characters, 1)
    free_strat.run(characters, 2)
    suffix.run(characters, False)
    sys.stdout=sys.__stdout__
"""    # run prism-games with lots of memory, hardcoded prism-games location on SAND
    os.system("../../../../../../usr/local/prism-games-2.0.beta3-linux64/bin/prism -cuddmaxmem 100g -javamaxmem 100g smg.prism smg_props.props -prop 4 -s > log.txt")
    p1_opt = find_prev_result()
    os.system("../../../../../../usr/local/prism-games-2.0.beta3-linux64/bin/prism -cuddmaxmem 100g -javamaxmem 100g smg.prism smg_props.props -prop 5 -s > log.txt")
    p2_opt = find_prev_result()
    return p1_opt, p2_opt"""

# Generates grid of opt(win) for all permutations of G
def generate_opt_grid():
    # First pair (CAPS) is team for whom probOpt is calculated
    global KAkw, KAwa, KAka, KWkw, KWwa, KWka, WAkw, WAwa, WAka
    print "Calculating optimalities, this may take some time...",
    KAkw, KWka = optimality(["K", "A", "K", "W"])
    KAwa, WAka = optimality(["K", "A", "W", "A"])
    KWwa, WAkw = optimality(["K", "W", "W", "A"])
    KAka, _ = optimality(["K", "A", "K", "A"])
    KWkw, _ = optimality(["K", "W", "K", "W"])
    WAwa, _ = optimality(["W", "A", "W", "A"])
    # Display results
    print "win\\vs\t|KA\t\t|KW\t\t|WA"
    print "KA\t|"+str(KAka)+"\t|"+str(KAkw)+"\t|"+str(KAwa)
    print "KW\t|"+str(KWka)+"\t|"+str(KWkw)+"\t|"+str(KWwa)
    print "WA\t|"+str(WAka)+"\t|"+str(WAkw)+"\t|"+str(WAwa)

# Takes a prob. and a pairing and displays prob. and probOpt for comparison
def above_opt(probability, opposition, challenger):
    opt = 0
    if challenger == ["K","A"]:
        if opposition == ["K","W"]:
            opt = KAkw
        elif opposition == ["W","A"]:
            opt = KAwa
        else:
            opt = KAka
    elif challenger == ["K","W"]:
         if opposition == ["K","W"]:
             opt = KWkw
         elif opposition == ["W","A"]:
             opt = KWwa
         else:
             opt = KWka
    else:
        if opposition == ["K","W"]:
            opt = WAkw
        elif opposition == ["W","A"]:
            opt = WAwa
        else:
            opt = WAka
    print "probOpt = " + str(probability) + ", optimal = " + str(opt)
    # return probability > opt              OLD: former (dumb) main while-loop check

# Compare adversary with relevant recent files to see if we're in a loop.
def adversary_is_unique(it):
    f1 = "adversarial_strategy_" + str(it-1) + ".txt"
    if it > 6:                                      # First adversaries can't be a duplicates
        print "Comparing generated adversary...",
        for comp in range(it-2, -1, -1):             # Compares {it} with {it-1, it-2, ... 1}
            f2 = "adversarial_strategy_" + str(comp) + ".txt"
            if filecmp.cmp(f1, f2, shallow=False):  # false flag ensures deep comparison (not just file paths!)
                print "adversary " + str(it-1) + " is equivalent to adversary " + str(comp)
                return False
    print "adversary is unique, continuing"
    return True

# Takes last adversarial opponents and finds new best opponents and greatest probAdv
def flip_and_run(it, opponent):
    print opponent, "is opponent team in iteration:", str(it)
    best_pair = None
    best_score = 0.0
    # build model for each opponent
    for i in range(len(possible_pairs)):
        sys.stdout=open("it"+str(it)+"vs"+possible_pairs[i][0]+possible_pairs[i][1]+".prism","w")
        if it % 2 == 1:
            matchup = possible_pairs[i]+opponent
            prefix.run(matchup, "mdp", False)           # False as |I| = 1
            free_strat.run(matchup, 1)
            sys.stdout=sys.__stdout__
            os.system("cat adversarial_strategy_"+str(it-1)+".txt >> it"+str(it)+"vs"+possible_pairs[i][0]+possible_pairs[i][1]+".prism")
            sys.stdout=open("it"+str(it)+"vs"+possible_pairs[i][0]+possible_pairs[i][1]+".prism","a")
        else:
            matchup = opponent+possible_pairs[i]
            prefix.run(matchup, "mdp", False)
            sys.stdout=sys.__stdout__
            os.system("cat adversarial_strategy_"+str(it-1)+".txt >> it"+str(it)+"vs"+possible_pairs[i][0]+possible_pairs[i][1]+".prism")
            sys.stdout=open("it"+str(it)+"vs"+possible_pairs[i][0]+possible_pairs[i][1]+".prism","a")
            free_strat.run(matchup, 2)
        suffix.run(matchup, False)                      # False as |I| = 1
        sys.stdout=sys.__stdout__
        os.system("prism -javamaxmem 100g -s it"+str(it)+"vs"+possible_pairs[i][0]+possible_pairs[i][1]+".prism props.props -prop "+str(2-it%2)+" > log.txt")
        pair_result = find_prev_result()
        print "ProbAdv_"+str(2-(it%2))+"(" + str(matchup) + ") = " + str(pair_result)
        # find_max for opponent and probAdv
        if pair_result > best_score:
            best_score = pair_result
            best_pair = possible_pairs[i]
    print best_pair, "found as adversarial team, generating strategy..."
    # Write old_adv VS best_opp to file with multiple i in I for adversary calculation
    sys.stdout = open("it"+str(it)+"_adv.prism", "w")
    if it % 2 == 1:
        matchup = best_pair + opponent
        prefix.run(matchup, "mdp", True)                # True as |I| > 1
        free_strat.run(matchup, 1)
        sys.stdout=sys.__stdout__
        os.system("cat adversarial_strategy_"+str(it-1)+".txt >> it"+str(it)+"_adv.prism")
        sys.stdout=open("it"+str(it)+"_adv.prism","a")
        suffix.run(matchup, True)                       # True as |I| > 1
    else:
        matchup = opponent + best_pair
        prefix.run(matchup, "mdp", True)
        sys.stdout=sys.__stdout__
        os.system("cat adversarial_strategy_"+str(it-1)+".txt >> it"+str(it)+"_adv.prism")
        sys.stdout=open("it"+str(it)+"_adv.prism","a")
        free_strat.run(matchup, 2)
        suffix.run(matchup, True)
    sys.stdout=sys.__stdout__
    os.system("prism -s -javamaxmem 100g it"+str(it)+"_adv.prism props.props -prop "+str(2-it%2)+" -s -exportadvmdp tmp.tra -exportstates tmp.sta > log.txt")
    sys.stdout = open("adversarial_strategy_"+str(it)+".txt", "w")
    # Write adversary to file (adversarial_strategy_it)
    educate_strat.run(matchup, "tmp", 2-(it%2))
    sys.stdout=sys.__stdout__
    return best_pair, best_score

for pair in [["K","A"],["K","W"],["A","W"]]:
    characters = ["K", "A"] + pair

    sys.stdout=open("smg"+pair[0]+pair[1]+.prism","w")
    smgPrefix.run(characters)
    free_strat.run(characters, 1)
    free_strat.run(characters, 2)
    suffix.run(characters, False)
    sys.stdout=sys.__stdout__



"""
# Main: setup
global possible_pairs
generate_opt_grid()
possible_pairs = [["K","A"],["K","W"],["A","W"]]
best_score = 0.0
best_pair = None
chosen_seed_team = possible_pairs[2]                    # Change this value (0-2) for different seed teams
print chosen_seed_team, "chosen as the seed, calculating adversaries..."

# Find adversary of seed strategy:
    # generate file: seed_v_free for all opponents
    # calculate probAdv_2 and find_max() for greatest probAdv and 'best' opponent pair
for i in range(len(possible_pairs)):
    sys.stdout=open("seed"+str(i)+".prism","w")
    matchup = chosen_seed_team + possible_pairs[i]
    prefix.run(matchup, "mdp", False)
    seed_strat.run(matchup, 1, "none")           # "none" as no preferred action.
    free_strat.run(matchup, 2)
    suffix.run(matchup, False)
    sys.stdout=sys.__stdout__
    os.system("prism -s -javamaxmem 100g seed"+str(i)+".prism props.props -prop 2 > log.txt")
    pair_result = find_prev_result()
    print "ProbAdv_2(" + str(matchup) + ") = " + str(pair_result)
    if pair_result > best_score:
        best_score = pair_result
        best_pair = possible_pairs[i]

# Generate first adversary (adversarial_strategy_0.txt)
    # Create model with multiple i in I
    # write adversary to file using tmp files generated by PRISM calculation
print best_pair, "found as adversarial team, generating strategy..."
matchup = chosen_seed_team + best_pair
sys.stdout = open("seed_v_adv.prism", "w")
prefix.run(matchup, "mdp", True)
seed_strat.run(matchup, 1, "none")
free_strat.run(matchup, 2)
suffix.run(matchup, True)
sys.stdout=sys.__stdout__
os.system("prism -cuddmaxmem 100g -javamaxmem 100g seed_v_adv.prism props.props -prop 2 -s -exportadvmdp tmp.tra -exportstates tmp.sta > log.txt")
sys.stdout = open("adversarial_strategy_0.txt", "w")
educate_strat.run(matchup, "tmp", 2)
sys.stdout=sys.__stdout__

# Core loop
iteration = 1
old_opponents = chosen_seed_team
while adversary_is_unique(iteration):
    #above_opt(best_score, old_opponents, best_pair)       #prob, op, chal
    old_opponents = best_pair
    best_pair, best_score = flip_and_run(iteration, best_pair)
    iteration+=1

# End
print "Loop found, run terminated."
"""
