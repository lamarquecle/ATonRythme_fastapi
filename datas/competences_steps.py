import json

PATH_COMPETENCES = "./BDDATonRythme/competences_ensembles_operation.json"
with open(PATH_COMPETENCES, 'r', encoding="utf-8") as f:
    # Charge le contenu du fichier JSON en tant qu'objet Python
    competences = json.load(f)
    print(len(competences))
    competences = list(filter(lambda x : "_" not in list(x.keys()), competences))
    print(len(competences))
    competences_uuid = [competence["uuid"].split(" ")[0] for competence in competences]
    print(len(competences_uuid))

def is_ancestors_group_valid(competence_to_learn, competences_learned_uuid) -> bool :
    if not competence_to_learn["ancestors"] : return True
    for ancestors_group in competence_to_learn["ancestors"] :
        if all(ancestor in competences_learned_uuid for ancestor in ancestors_group) :
            return True
    return False

def get_ancestor_name_from_uuid(ancestor, competences_learned):
    for competence_learned in competences_learned :
        uuid = competence_learned["uuid"].split(" ")[0]
        if ancestor==uuid :
            return competence_learned["knowledge_small"]

    return "ERROR : the ancestor isn't find in competences"


def print_competences_with_ancestors(ancestors_groups, competences) -> None :
    for ancestors_group in ancestors_groups :
        print(f"   {ancestors_group}")
        for ancestor in ancestors_group :
            ancestor_name = get_ancestor_name_from_uuid(ancestor, competences)
            print(f"       {ancestor:<15} - {ancestor_name}")

MAX_STEPS = 20
competences_learned = []
competences_to_learn = competences
for step in range(50):
    print("-"*30)
    print(f'{f"  step {step}  ":-^30}')
    print("-"*30)

    competences_learned  = competences_learned
    competences_to_learn = competences_to_learn


    competences_learned_uuid = list(map(lambda x : x["uuid"].split(" ")[0], competences_learned))


    new_competences_to_learn = []
    new_competences_learned = False
    for i, competence_to_learn in enumerate(competences_to_learn) :
        #if i > 5 : break

        competence_to_learn_uuid = competence_to_learn["uuid"].split(" ")[0]

        can_be_learn = is_ancestors_group_valid(competence_to_learn, competences_learned_uuid)

        if can_be_learn :
            new_competences_learned = True
            competences_learned += [competence_to_learn]
            print(competence_to_learn["uuid"].split(" ")[0], competence_to_learn["knowledge_small"])
            ancestors_groups = competence_to_learn["ancestors"]
            print_competences_with_ancestors(ancestors_groups, competences_learned + competences_to_learn)
        else :
            new_competences_to_learn += [competence_to_learn]

    competences_learned  = competences_learned
    competences_to_learn = new_competences_to_learn

    if not new_competences_learned :
        print(f"Can be learn from other knowledge : {len(competences_learned)}")
        print(f"ERROR : Impossible to learn these knowledge one day : {len(competences_to_learn)}")
        break


print("-"*80)
print(f'{f"  competences_to_learn  ":-^80}')
print("-"*80)
for competence_to_learn in competences_to_learn :
    print(f"{competence_to_learn['uuid'].split(' ')[0]:<15}{competence_to_learn['knowledge_small']}")
    ancestors_groups = competence_to_learn["ancestors"]
    print_competences_with_ancestors(ancestors_groups, competences_learned + competences_to_learn)





