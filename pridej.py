import csv
import json
import sys
import os
import random
import string

from textwrap import dedent
from typing import Iterator

def random_id(k=10):
	letters = random.choices(string.ascii_lowercase + string.digits, k=k)
	return ''.join(letters)

def process_questions(file) -> Iterator[dict]:
	cols = set('question,answer,topic,difficulty,may_change,more_info'.split(','))
	with open(file, 'rt', encoding='utf8') as f:
		cr = csv.DictReader(f)

		splittable = ('answer', 'more_info')

		for q in cr:
			assert set(q.keys()) == cols, f'ocekavame tyhle sloupce: {", ".join(cols)}'
			q = {k: v.strip() for k, v in q.items()}

			if not q['answer']:
				continue # TODO

			for col in splittable:
				if ';' in q[col]:
					q[col] = [j.strip() for j in q[col].split(';')]

			diff = q['difficulty']
			assert diff.isdigit()
			diff = int(diff)
			assert diff >= 1 and diff <= 5, f'narocnost neni cislo mezi 1 a 5: {diff}'

			assert q['may_change'] in ('yes', 'no')
			q['may_change'] = q['may_change'] == 'yes'

			yield {
				'id': random_id(),
				'question': q['question'],
				'answer': q['answer'],
				'topic': q['topic'] or None,
				'difficulty': diff,
				'may_change': q['may_change'],
				'more_info': q['more_info'],
			}

if __name__ == '__main__':
	if len(sys.argv) != 2:
		instructions = '''
		Pro pridani otazek je treba zavolat tento skript s jednim argumentem - nazvem
		CSV souboru, ze ktereho se otazky nactou.

		Soubor musi mit nasledujici sloupce:
		- question: polozena otazka (string)
		- answer: odpoved na otazku (string nebo list stringu, pokud je vice moznosti)
		- topic: tema otazky (string)
		- difficulty: narocnost otazky (int, 1-5, 1 je nejlehci)
		- may_change: zda se odpoved muze v case zmenit (string, yes/no)
		- more_info: odkazy na zdroje ci dalsi informace (string nebo list stringu)
		'''

		print(dedent(instructions))
		sys.exit(1)
		

	questions = process_questions(sys.argv[1])
	tdir = 'otazky'
	os.makedirs(tdir, exist_ok=True)
	for q in questions:
		tfn = os.path.join(tdir, q['id'][0] + '.json')
		if not os.path.isfile(tfn):
			with open(tfn, 'w') as fw:
				fw.write('[]')

		with open(tfn, 'rt', encoding='utf8') as f:
			questions = json.load(f)

		with open(tfn, 'wt', encoding='utf8') as fw:
			questions.append(q)
			json.dump(questions, fw, indent=2, ensure_ascii=False)
	