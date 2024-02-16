import json
import argparse

def avg_mmlu_score(scores:dict):
    accs = []
    for key, value in scores.items():
        if not key.startswith('mmlu'):
            continue

        if 'acc,none' not in value:
            continue

        acc_none = value['acc,none']
        accs.append(acc_none)

    return sum(accs) / len(accs)

def nq_score(scores:dict):
    return scores['nq_open']['exact_match,remove_whitespace']

def triviaqa_score(scores:dict):
    return scores['triviaqa']['exact_match,remove_whitespace']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str)
    args = parser.parse_args()

    print(f'Results for model: {args.model}')
    model_name = args.model.replace('/', '__')
    result_filename = f'result_scores-{model_name}.json'
    with open(result_filename, 'r') as f:
        scores = json.load(f)

    print(f'Average MMLU score: {avg_mmlu_score(scores)}')
    print(f'NQ score: {nq_score(scores)}')
    print(f'TriviaQA score: {triviaqa_score(scores)}')

if __name__ == '__main__':
    main()
