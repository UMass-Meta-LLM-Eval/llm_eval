from termcolor import colored

INSPECT_CLI = f'''
{colored("Benchmark", "red")} : {{benchmark_name}}
{colored("Model", "red")}     : {{model_name}}
{colored("Question", "red")}  : {{question}}
{colored("Prompt", "red")}    :
{{prompt}}
{colored("References", "red")}:
{{references}}
{colored("Response", "red")}  :
{{response}}
{colored("Evaluations", "red")}:{{evaluations}}
'''.strip()
"""Template string for printing the inspection result in CLI."""

INSPECT_MD = '''
<span style="color:red">**Benchmark:**</span> {benchmark_name}

<span style="color:red">**Model:**</span> {model_name}

<span style="color:red">**Question:**</span> {question}

<span style="color:red">**Prompt:**</span>
```
{prompt}
```

<span style="color:red">**References:**</span>
{references}

<span style="color:red">**Response:**</span>
```
{response}
```

<span style="color:red">**Evaluations:**</span>
{evaluations}
'''.strip()
"""Template string for saving the inspection result in a markdown file."""