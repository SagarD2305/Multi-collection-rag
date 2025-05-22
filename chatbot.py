import openai
import os
from rag.retrieval import retrieve_data
from rag.memory import Memory
from rag.vector_store import VectorStore
from datetime import datetime

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))

class Chatbot:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.memory = Memory()
        self.last_topic = None

    def find_data_by_date(self, data, target_date):
        """Find data entries matching a specific date."""
        target_date = target_date.split('T')[0]  # Get just the date part
        return [item for item in data if item.get('timestamp', '').startswith(target_date)]

    def extract_date_from_query(self, query):
        """Extract date from query and return in YYYY-MM-DD format."""
        query = query.lower()
        if "january 1st" in query or "jan 1" in query:
            return "2023-01-01"
        elif "january 2nd" in query or "jan 2" in query:
            return "2023-01-02"
        elif "january 3rd" in query or "jan 3" in query:
            return "2023-01-03"
        return None

    def generate_suggestions(self, query, retrieved_data):
        """Generate proactive suggestions based on the current context."""
        suggestions = []
        
        # Extract date from query
        target_date = self.extract_date_from_query(query)

        # Filter data by date if specified
        if target_date:
            date_data = self.find_data_by_date(retrieved_data, target_date)
        else:
            date_data = retrieved_data

        # Generate suggestions based on available data
        for item in date_data:
            if "steps" in item and "steps" not in query.lower():
                suggestions.append(f"Would you like to know how many steps you took on {item['timestamp']}?")
            
            if "heart_rate" in item and "heart rate" not in query.lower():
                suggestions.append(f"Would you like to know your heart rate on {item['timestamp']}?")
            
            if "place" in item and "location" not in query.lower() and "where" not in query.lower():
                suggestions.append(f"Would you like to know where you were on {item['timestamp']}?")
            
            if "preferences" in item and "preferences" not in query.lower():
                suggestions.append(f"Would you like to know about {item['name']}'s preferences?")
            
            if "category" in item and item["category"] == "movies" and "movie" not in query.lower():
                suggestions.append(f"Would you like to know about your movie ratings?")

        # Add time-based suggestions
        if target_date:
            next_day = datetime.strptime(target_date, "%Y-%m-%d").replace(day=datetime.strptime(target_date, "%Y-%m-%d").day + 1)
            next_day_str = next_day.strftime("%Y-%m-%d")
            suggestions.append(f"Would you like to know what happened on {next_day_str}?")

        return suggestions[:3]  # Return top 3 suggestions

    def generate_fallback_response(self, query, retrieved_data):
        """Generate a fallback response when API is unavailable."""
        query = query.lower()
        
        # Extract date from query
        target_date = self.extract_date_from_query(query)
        
        # Filter data by date if specified
        if target_date:
            retrieved_data = self.find_data_by_date(retrieved_data, target_date)
            if not retrieved_data:
                return f"I couldn't find any data for {target_date}. Please try a different date."
        
        # Generate response based on query type
        if "steps" in query:
            for item in retrieved_data:
                if "steps" in item:
                    return f"Based on the data, you took {item['steps']} steps on {item['timestamp']}."
        
        if "heart rate" in query:
            for item in retrieved_data:
                if "heart_rate" in item:
                    return f"Your heart rate was {item['heart_rate']} on {item['timestamp']}."
        
        if "location" in query or "where" in query:
            for item in retrieved_data:
                if "place" in item:
                    return f"You were in {item['place']} on {item['timestamp']}."
        
        if "preferences" in query:
            for item in retrieved_data:
                if "preferences" in item:
                    return f"User preferences include: {', '.join(item['preferences'])}."
        
        if "movie" in query:
            for item in retrieved_data:
                if "category" in item and item["category"] == "movies":
                    return f"You have rated {item['item']} with a rating of {item['rating']}."
        
        # Generic response if no specific data is found
        return f"I found some data related to your query: {retrieved_data}. However, I'm currently operating in a limited mode. Please try asking about specific data points like steps, heart rate, or location."

    def generate_response(self, query):
        try:
            # Retrieve relevant data
            retrieved_data = retrieve_data(query, self.vector_store)
            
            # Extract date and filter data if date is specified
            target_date = self.extract_date_from_query(query)
            if target_date:
                retrieved_data = self.find_data_by_date(retrieved_data, target_date)
                if not retrieved_data:
                    return f"I couldn't find any data for {target_date}. Please try a different date."
            
            # Get memory context
            memory_context = self.memory.get_history()
            
            # Prepare context
            if retrieved_data:
                context = f"Retrieved Data: {retrieved_data}\nMemory Context: {memory_context}"
            else:
                context = f"No specific data found. Memory Context: {memory_context}"
            
            try:
                # Generate response using OpenAI
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided data. Be concise and direct in your responses."},
                        {"role": "user", "content": f"Context: {context}\nQuery: {query}\nPlease provide a clear and concise response based on the data."}
                    ],
                    max_tokens=150
                )
                
                # Extract the response text
                response_text = response.choices[0].message.content.strip()
                
            except Exception as api_error:
                # If API call fails, use fallback response
                response_text = self.generate_fallback_response(query, retrieved_data)
            
            # If no response, provide a default response
            if not response_text:
                response_text = "I'm sorry, I couldn't generate a specific response. Could you please rephrase your question?"
            
            # Generate proactive suggestions
            suggestions = self.generate_suggestions(query, retrieved_data)
            if suggestions:
                response_text += "\n\nProactive Suggestions:\n" + "\n".join(suggestions)
            
            # Update memory
            self.memory.add_interaction(query, response_text)
            return response_text
            
        except Exception as e:
            error_response = f"I encountered an error: {str(e)}. Please try again."
            self.memory.add_interaction(query, error_response)
            return error_response

if __name__ == '__main__':
    # Example usage
    vector_store = VectorStore()
    # Assume vector_store is already populated
    chatbot = Chatbot(vector_store)
    query = "What's the weather like?"
    response = chatbot.generate_response(query)
    print(f'Query: {query}\nResponse: {response}') 