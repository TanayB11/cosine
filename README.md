# cosine
Private semantic search for your Obsidian vault

---

- [About](#about)
- [Examples](#examples)
- [Setup](#setup)


## About
Semantic search allows you to search for content based on its meaning, rather
than just matching keywords. You'll find relevant information, even if it uses
different terminology.

Most solutions for semantic search in Obsidian rely on OpenAI's API, but I
don't want to upload my private Obsidian vault to an external server.

Cosine runs locally on your own machine (or server). It uses [Langchain](https://www.langchain.com/),
[LanceDB](https://lancedb.com/), [FastAPI](https://fastapi.tiangolo.com/),
and [Sentence Transformers](https://www.sbert.net/).

## Setup
Cosine currently consists of a simple CLI `cosine.py` and a FastAPI server.

First, populate `.env`:
```
VAULT_PATH=/path/to/your/vault
```

Then, install dependencies:
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

With the virtual environment activated, there are two options to run Cosine:
```
# the easy way: run the TUI and server together, use Ctrl-C to stop
make
```

Alternatively, use the CLI. Note that table formatting is optimized for
markdown output, so outputs might look weird.
```
# first, start the server
cd server
make prod

# run these in a separate terminal window
python upload ~/path/to/obsidian/vault
python cosine.py search "Why is digital privacy important?"
```

```
+-----------------------------+------------------------------------------------------------------------+
| File                        | Text                                                                   |
+=============================+========================================================================+
| Permanent Record.md         | A spreadsheet containing every scrap of data about you would pose a    |
|                             | mortal hazard. Imagine it: all the secrets big and small that could    |
|                             | end your marriage, end your career, poison even your closest           |
|                             | relationships, and leave you broke, friendless, and in prison. —       |
|                             | location: 2730 tref-26363  citizens of pluralistic, technologically    |
|                             | sophisticated democracies feel that they have to justify their desire  |
|                             | for privacy and frame it as a right. But citizens of democracies don’t |
|                             | have to justify that desire—the state, instead, must justify its       |
|                             | violation. — location: 2859 ^ref-48542  Just because this or that      |
+-----------------------------+------------------------------------------------------------------------+
| Permanent Record.md         | It was heinous to be so inextricably, technologically bound to a past  |
|                             | that I fully regretted but barely remembered. — location: 1322         |
|                             | ^ref-17348  In the context of the US government, however,              |
|                             | restructuring your intelligence agencies so that your most sensitive   |
|                             | systems were being run by somebody who didn’t really work for you was  |
|                             | what passed for innovation. — location: 1551 ^ref-63921  It was        |
|                             | particularly bizarre to me that most of the systems engineering and    |
|                             | systems administration jobs that were out there were private, because  |
|                             | these positions came with almost universal access to the employer’s    |
+-----------------------------+------------------------------------------------------------------------+
```

