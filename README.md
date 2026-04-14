# 🗄️ Text-to-SQL Agent

A local AI agent that takes a plain English question and turns it into a SQL query — then runs it against a real SQLite database and shows you the results.

No cloud, no API keys. Everything runs on your machine using Ollama.

---

## 💡 How It Works

```
You type a question
        ↓
Ollama (gemma4:e2b) reads the DB schema and writes a SQL query
        ↓
The query runs against store.db (SQLite)
        ↓
Results are printed to your notebook
```

---

## 🗂️ Project Structure

```
project/
├── agent.py      # the Text-to-SQL agent
└── store.db      # auto-generated when you run setup_db.py
```

---

## 🛢️ Database Schema

Four tables that can be joined together for interesting queries:

| Table | Columns |
|---|---|
| `suppliers` | id, name, country, lead_time_days |
| `products` | id, name, category, price, stock, supplier_id |
| `customers` | id, name, city, joined_date |
| `orders` | id, product_id, customer_id, quantity, order_date, status |

**Order statuses:** `completed` · `pending` · `cancelled`

The database comes pre-loaded with:
- 5 suppliers across Italy, Germany, China, USA, France
- 15 products across Electronics, Furniture, Stationery, and Accessories
- 50 customers spread across 10 European cities
- 200 randomly generated orders from 2023–2024

---

## ⚙️ Requirements

**Python packages:**
```bash
pip install llama-index-llms-ollama
```

**Ollama** must be running locally with these models pulled:
```bash
ollama pull gemma4:e2b
```

---

## 🚀 Quick Start

If you are using a **Jupyter notebook**, run these two cells in order:

**Cell 1 — Set up the database:**
```python
# paste the full contents of setup_db.py here and run it
# you should see: ✅ store.db ready — 15 products, 50 customers, 200 orders
```

**Cell 2 — Run the agent:**
```python
# paste the full contents of agent.py here and run it
```

If you are using **plain Python scripts**, just run:
```bash
python agent.py
```
The agent calls `setup()` automatically on startup.

---

## 💬 Example Questions

```python
ask("Which products are out of stock?")
ask("What are the top 5 products by total revenue from completed orders?")
ask("Which supplier has the longest lead time?")
ask("How many orders were placed per month in 2024?")
ask("Which customers have placed more than 5 orders?")
ask("What is the average order quantity per product category?")
```

**Example output:**
```
Question: Which products are out of stock?
SQL: SELECT name, category, stock FROM products WHERE stock = 0
Results: 2 rows
  {'name': 'USB-C Hub', 'category': 'Electronics', 'stock': 0}
  {'name': 'Webcam HD', 'category': 'Electronics', 'stock': 0}
```

---

## 🧠 How the Agent Works (Code Walkthrough)

### `get_sql(question)` — asks the LLM to write SQL
Sends your question plus the database schema to Ollama. The model returns a SQL query. If the model wraps it in markdown backticks (` ```sql ... ``` `), those are automatically stripped out so the query runs cleanly.

### `run_sql(sql)` — runs the query against SQLite
Opens `store.db`, executes the SQL, and returns the results as a list of dictionaries — one dictionary per row.

### `ask(question)` — the function you actually call
Calls `get_sql()` then `run_sql()`, and prints everything: the generated SQL and the results. If the SQL has an error, it prints the error message instead of crashing.

---

## 🔧 Customisation

**Change the model:**
```python
llm = Ollama(model="llama3.2", request_timeout=300.0)
```

**Add your own data:**  
Edit the `suppliers`, `products`, `customers`, and `orders` lists in `setup_db.py`, then re-run `setup()`.

**Ask your own questions:**
```python
ask("Which city has the most customers?")
ask("What is the most expensive product per category?")
```

---

## 🔮 What to Build Next

- **Self-correction loop** — if the SQL fails, feed the error back to the LLM and ask it to fix it
- **Multi-turn chat** — keep conversation history so follow-up questions like *"now filter that by Milan"* work
- **RAG + SQL hybrid** — combine this with a vector store so you can query both structured and unstructured data in one question
