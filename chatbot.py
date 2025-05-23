import openai
import os
from rag.retrieval import retrieve_data
from rag.memory import Memory
from rag.vector_store import VectorStore
from datetime import datetime

# Initialize OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY', '')

class Chatbot:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.memory = Memory()
        self.last_topic = None

    def find_data_by_date(self, data, target_date):
        """Find data entries matching a specific date."""
        if not data:
            return []
            
        # Handle different data types
        filtered_data = []
        for item in data:
            # Skip items without timestamp if we're looking for date-specific data
            if target_date and 'timestamp' not in item:
                continue
                
            # For date-specific queries
            if target_date and 'timestamp' in item:
                item_date = item['timestamp'].split('T')[0]
                if item_date == target_date:
                    filtered_data.append(item)
            # For non-date specific queries (like preferences)
            elif not target_date:
                filtered_data.append(item)
                
        return filtered_data

    def extract_date_from_query(self, query):
        query = query.lower()
        date_mapping = {
            "january 1st": "2023-01-01",
            "jan 1": "2023-01-01",
            "january 2nd": "2023-01-02",
            "jan 2": "2023-01-02",
            "january 3rd": "2023-01-03",
            "jan 3": "2023-01-03",
            "january 4th": "2023-01-04",
            "jan 4": "2023-01-04",
            "january 5th": "2023-01-05",
            "jan 5": "2023-01-05",
            "january 6th": "2023-01-06",
            "jan 6": "2023-01-06",
            "january 7th": "2023-01-07",
            "jan 7": "2023-01-07",
            "january 8th": "2023-01-08",
            "jan 8": "2023-01-08"
        }
        
        for date_text, date_value in date_mapping.items():
            if date_text in query:
                return date_value
        return None

    def generate_suggestions(self, query, retrieved_data):
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
                ts = item.get('timestamp', item.get('date', 'an unknown date'))
                suggestions.append(f"Would you like to know how many steps you took on {ts}?")
            if "heart_rate" in item and "heart rate" not in query.lower():
                ts = item.get('timestamp', item.get('date', 'an unknown date'))
                suggestions.append(f"Would you like to know your heart rate on {ts}?")
            if "place" in item and "location" not in query.lower() and "where" not in query.lower():
                ts = item.get('timestamp', item.get('date', 'an unknown date'))
                suggestions.append(f"Would you like to know where you were on {ts}?")
            if "preferences" in item and "preferences" not in query.lower():
                name = item.get('name', 'the user')
                suggestions.append(f"Would you like to know about {name}'s preferences?")
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
                    ts = item.get('timestamp', item.get('date'))
                    if not ts:
                        ts = target_date if 'target_date' in locals() and target_date else None
                    if ts:
                        return f"Based on the data, you took {item['steps']} steps on {ts}."
                    else:
                        return f"Based on the data, you took {item['steps']} steps."

        if "heart rate" in query:
            for item in retrieved_data:
                if "heart_rate" in item:
                    ts = item.get('timestamp', item.get('date'))
                    if not ts:
                        ts = target_date if 'target_date' in locals() and target_date else None
                    if ts:
                        return f"Your heart rate was {item['heart_rate']} on {ts}."
                    else:
                        return f"Your heart rate was {item['heart_rate']}."

        if "location" in query or "where" in query:
            for item in retrieved_data:
                if "place" in item:
                    ts = item.get('timestamp', item.get('date'))
                    if not ts:
                        ts = target_date if 'target_date' in locals() and target_date else None
                    if ts:
                        return f"You were in {item['place']} on {ts}."
                    else:
                        return f"You were in {item['place']}."
        
        if "preferences" in query:
            for item in retrieved_data:
                if "preferences" in item and "name" in item:
                    return f"{item['name']}'s preferences include: {', '.join(item['preferences'])}."
        
        if "movie" in query:
            for item in retrieved_data:
                if "category" in item and item["category"] == "movies":
                    return f"You have rated {item['item']} with a rating of {item['rating']}."
        
        # Handle age and weight queries
        if "age" in query or "weight" in query:
            for item in retrieved_data:
                age = item.get("age")
                weight = item.get("weight")
                if age is not None and weight is not None:
                    return f"Your age is {age} and your weight is {weight}."
                elif age is not None:
                    return f"Your age is {age}."
                elif weight is not None:
                    return f"Your weight is {weight}."
        
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
            
            # Try to answer directly from data (fallback logic)
            direct_answer = self.generate_fallback_response(query, retrieved_data)
            # If fallback logic gives a specific answer (not the generic fallback), use it
            if not direct_answer.startswith("I found some data related to your query:"):
                # Add suggestions if available
                suggestions = self.generate_suggestions(query, retrieved_data)
                if suggestions:
                    direct_answer += "\n\nProactive Suggestions:\n" + "\n".join(suggestions)
                self.memory.add_interaction(query, direct_answer)
                return direct_answer

            # If no direct answer, use OpenAI
            memory_context = self.memory.get_history()
            context = f"Retrieved Data: {retrieved_data}\nMemory Context: {memory_context}" if retrieved_data else f"No specific data found. Memory Context: {memory_context}"
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided data. Be concise and direct in your responses."},
                        {"role": "user", "content": f"Context: {context}\nQuery: {query}\nPlease provide a clear and concise response based on the data."}
                    ],
                    max_tokens=150
                )
                response_text = response.choices[0].message.content.strip()
            except Exception as api_error:
                response_text = direct_answer  # fallback already generic

            # Add suggestions if available
            suggestions = self.generate_suggestions(query, retrieved_data)
            if suggestions:
                response_text += "\n\nProactive Suggestions:\n" + "\n".join(suggestions)
            self.memory.add_interaction(query, response_text)
            return response_text

        except Exception as e:
            error_response = f"I encountered an error: {str(e)}. Please try again."
            self.memory.add_interaction(query, error_response)
            return error_response

if __name__ == '__main__':

    vector_store = VectorStore()

    chatbot = Chatbot(vector_store)
    query = "What's the weather like?"
    response = chatbot.generate_response(query)
    print(f'Query: {query}\nResponse: {response}')
