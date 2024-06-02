import urllib.parse
from llama_index.core.tools.tool_spec.base import BaseToolSpec
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import urllib


app_id = 'KWW3UE-KE799U2QKY'


class MathsToolSpec(BaseToolSpec):
    '''Maths Tutor Tool Spec'''

    spec_functions = [
        "graph_plot", 
        "show_steps", 
        "calculator"
    ]

    def __init__(self, wolfram_app_id: str = app_id):
        self.wolfram_app_id = wolfram_app_id

    def graph_plot(self, query: str) -> str:
        '''
        function for plotting the graph for the given mathematical function or equation, in text format.

        Args:
            query: str - the query of mathematical function or equation, which needs to plotted
        Returns:
            str - whether the plot is successfully plotted or not.
        '''
        query = "plot " + query
        query = urllib.parse.quote_plus(query)
    # URL for the Wolfram Alpha API
        url = f'http://api.wolframalpha.com/v2/query?input={query}&format=image,plaintext&output=JSON&appid={self.wolfram_app_id}'

        # Send the request to the API
        response = requests.get(url)
        data = response.json()

        try:
            # Extract the image URL from the response
            pods = data['queryresult']['pods']
            image_url = None
            for pod in pods:
                if 'plot' in pod['title'].lower():
                    subpods = pod['subpods']
                    for subpod in subpods:
                        if 'img' in subpod:
                            image_url = subpod['img']['src']
                            break
                    if image_url:
                        break

            # Check if an image URL was found
            if image_url:
                # Download the image
                image_response = requests.get(image_url)
                img = Image.open(BytesIO(image_response.content))

                # Display the image using Matplotlib
                plt.imshow(img)
                plt.axis('off')  # Hide the axes
                plt.show()
                return "Plot succesfully plotted"
            else:
                return "No plot found in the query result."
        except Exception as e:
            print(e)
            return "No plot found"


    def show_steps(self, query: str) -> str:
        '''
        function for solving a mathematical expression or equation, and providing each steps for the solution.

        Args: 
            query: str - the mathematical query, in the form of expression or equation which needs to be solved
        Returns:
            str - solution with complete steps of solution
        '''
        query = urllib.parse.quote_plus(query)
        url = f'http://api.wolframalpha.com/v2/query?input={query}&podstate=Result__Step-by-step+solution&format=plaintext&output=JSON&appid={self.wolfram_app_id}'

        # Send the request to the API
        response = requests.get(url)
        data = response.json()

        # Extract the solution steps from the response
        message = ""
        steps = []
        pods = data['queryresult']['pods']
        for pod in pods:
            if 'Solution' in pod['title'] or 'Result' in pod['title'] or 'steps' in pod['title']:
                subpods = pod['subpods']
                for subpod in subpods:
                    if 'plaintext' in subpod:
                        steps.append(subpod['plaintext'])

        # Check if solution steps were found
        if steps:
            message += "Solution Steps:\n"
            for step in steps:
                message += step + "\n"
        else:
            message += "No solution steps found in the query result."
        
        return message

    def calculator(self, equation: str):
        '''
        fucntion for solving equation with precise calculation, and returns the solution of the equation or expression

        Args:
            equation: str - equation to be solved by the calculator
        Example inputs:
            "(7 * 12 ^ 10) / 321"
            "How many calories are there in a pound of strawberries"

        Returns:
            str - the solution of the equation or expression
        '''
        QUERY_URL_TMPL = "http://api.wolframalpha.com/v1/result?appid={app_id}&i={query}"
        QUERY_URL_TMPL_2 = "http://api.wolframalpha.com/v2/query?appid={app_id}&input={query}&output=json&includepodid=DecimalApproximation&format=plaintext"

        response = requests.get(
            QUERY_URL_TMPL.format(
                app_id=self.wolfram_app_id, query=urllib.parse.quote_plus(equation)
            )
        )

        if "/" in response.text:
            sec_response = response.text 
            try:
                response = requests.get(
                    QUERY_URL_TMPL_2.format(
                        app_id=self.wolfram_app_id, 
                        query=urllib.parse.quote_plus(equation)
                    )
                )

                response = json.loads(response.text)['queryresult']
                response = response['pods'][0]['subpods'][0]['plaintext'][:-1]

                return response 
            except Exception as e:
                print(e)
                return sec_response
        
        return response.text
    
