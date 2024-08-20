SUBJECTIVE_PROMPT = """
User question: {question}

Please gather relevant data and information to answer a mathematical query. This involves interpreting mathematical question, identifying main mathematical concept and related topics or prerequisites. 
Frame a clear and concise query that encapsulates the user's question, focusing on retrieving context or solutions related to the identified concept. 
Use the available tools or functions to perform a Google search and scrape the search results.

Plan and execute various Google search queries to gather the required information from the web. Ensure the query includes relevant keywords or phrases.

Use the google_search_scrape function to retrieve relevant context for different search queries.

You can generate write one or more search queries to retrieve relevant context.
"""

EQUATION_SOLVER_PROMPT = """

"""