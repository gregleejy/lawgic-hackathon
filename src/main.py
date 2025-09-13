import os
import sys
import json
from datetime import datetime
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv

# Import our modules
from term import extract_terms_from_query
from context import process_context

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def setup_gemini_model():
    """Initialize and configure the Gemini 2.5 Pro model"""
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    return model

def create_legal_analysis_prompt(user_query: str, legal_context: str) -> str:
    """Create a structured prompt for legal analysis using the appended context"""
    
    prompt = f"""You are a Singapore-qualified lawyer specializing in the Personal Data Protection Act (PDPA). 
You must analyze the legal scenario and provide a JSON-like structured response with the most relevant legal provisions.

LEGAL SCENARIO TO ANALYZE:
{user_query}

RELEVANT PDPA PROVISIONS AND CONTEXT:
The following legal provisions, definitions, schedules, and subsidiary legislation have been identified as relevant to this scenario:

{legal_context}

CRITICAL INSTRUCTIONS:
1. Analyze the legal scenario using ONLY the provided PDPA context above
2. Identify the most relevant legal provisions from the context provided
3. MAXIMUM 5 provisions, but output FEWER if there aren't enough relevant provisions
4. Use definitions, Fifth Schedule, and subsidiary legislation as SUPPORTING CONTEXT in your reasoning

STRICT KEY FORMAT RULES - ONLY THESE 3 FORMATS ARE ACCEPTED:

FORMAT 1: "S [number] [document name]" 
EXAMPLES: "S 21(1) PDPA", "S 21(1) and (2) PDPA", "Ss 21(5) and (7) PDPA"

FORMAT 2: "Reg [number] [document name]" 
EXAMPLES: "Reg 4 PDPR", "Regs 4 and 5 PDPR"

FORMAT 3: "para [reference] of [Schedule] [document name]" 
EXAMPLES: "para 1(a) of Fifth Schedule PDPA"

ABSOLUTELY PROHIBITED KEY FORMATS EXAMPLES:
Do not accept "Section 21(1) PDPA" (must use "S" not "Section")
Do not accept "Definition: personal data" (definitions are NOT keys)
Do not accept "Fifth Schedule" (schedules are NOT keys unless using para format)
Do not accept "Personal Data Protection Regulations" (not a key)
Do not accept "S 21 of PDPA" (missing document name in key)
Do not accept "21(1) PDPA" (missing "S")
Do not accept "Regulation 4" (must use "Reg" and include document name)

VALIDATION CHECKLIST - EVERY KEY MUST:
Correct: Start with "S " OR "Reg " OR "para "
Correct: End with document name (PDPA or PDPR)
Correct: Follow exact format patterns shown above
Correct: Never include "Section", "Definition:", or standalone "Schedule"

OUTPUT FORMAT - RETURN EXACTLY THIS STRUCTURE:
{{
    "[VALID KEY FORMAT ONLY]": "[Legal reasoning explaining why this provision is relevant to the scenario. Reference how it applies to the specific facts. You may reference definitions and other provisions as supporting context within this reasoning.]"
}}

REASONING REQUIREMENTS:
- Explain WHY each provision is relevant to the specific scenario
- Reference the actual facts from the user query
- Show how the provision applies to those facts
- Use definitions, schedules, and subsidiary legislation as supporting context within reasoning
- Be detailed and legally precise (3-4 sentences per provision)

EXAMPLE CORRECT OUTPUT:
{{
    "S 21(1) and (2) PDPA": "The facts are about an individual requesting access to their data, so S 21 PDPA is relevant. S 21(1) PDPA states that unless excluded by another section, an organisation must upon an individual's request provide that individual with the personal data. S 21(2) PDPA points to the Fifth Schedule which may exclude certain data from disclosure requirements.",
    "Ss 21(5) and (7) PDPA": "These provisions are relevant because they set out how the organisation must respond to the access request when some data can be provided and others cannot. S 21(5) PDPA covers situations where partial access is granted, and S 21(7) PDPA requires notification about information that was not provided.",
    "para 1(a) of Fifth Schedule PDPA": "This paragraph is directly relevant as it excludes opinion data kept solely for evaluative purposes from disclosure requirements, which would reasonably include performance appraisals requested in this scenario.",
    "Reg 4 PDPR": "This regulation sets out the procedural requirements for responding to access requests, providing specific implementation details for compliance with S 21 PDPA obligations."
}}

FINAL WARNING:
- If a key does not match the 3 approved formats exactly, DO NOT include it
- Only include provisions that exist in the provided context
- Return ONLY the JSON structure, no additional text
- Maximum 5 provisions total
- Each key MUST start with "S ", "Reg ", or "para " and end with document name"""

    return prompt

def analyze_legal_scenario(user_query: str, legal_context: str) -> str:
    """Use Gemini to analyze the legal scenario with the provided context"""
    try:
        model = setup_gemini_model()
        prompt = create_legal_analysis_prompt(user_query, legal_context)
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating legal analysis: {str(e)}"

def save_to_output_json(analysis_json: str, output_file: str = "output.json"):
    """Save only the clean JSON analysis to output.json file with hardcoded definition filtering"""
    try:
        # Clean the analysis_json string to extract just the JSON content
        analysis_clean = analysis_json.strip()
        
        # Remove markdown code block formatting if present
        if analysis_clean.startswith('```json'):
            analysis_clean = analysis_clean.replace('```json', '', 1)
        if analysis_clean.startswith('```'):
            analysis_clean = analysis_clean.replace('```', '', 1)
        if analysis_clean.endswith('```'):
            analysis_clean = analysis_clean.rsplit('```', 1)[0]
        
        analysis_clean = analysis_clean.strip()
        
        # Try to parse as JSON to validate it's valid JSON
        try:
            parsed_json = json.loads(analysis_clean)
            
            # HARDCODED FILTER: Remove any keys containing "Definition"
            keys_to_remove = [key for key in parsed_json.keys() if "Definition" in key]
            for key in keys_to_remove:
                parsed_json.pop(key)
                print(f"🚫 Removed definition key: {key}")
            
            # Save the filtered JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, indent=2, ensure_ascii=False)
                
        except json.JSONDecodeError:
            # If it's not valid JSON, save as plain text
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analysis_clean)
        
        print(f"✓ Analysis saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error saving to {output_file}: {str(e)}")

def process_query(user_query: str, save_output: bool = True) -> dict:
    """Process a single query and return results"""
    try:
        # Step 1: Extract key terms from the query
        print("Step 1: Extracting key legal terms...")
        key_terms = extract_terms_from_query(user_query)
        print(f"✓ Extracted {len(key_terms)} key terms: {', '.join(key_terms[:10])}")
        
        # Step 2: Process through context checks (1-4)
        print("\nStep 2: Processing through legal context checks...")
        print("  - Check 1: PDPA category matching...")
        print("  - Check 2: Interpretation definitions...")
        print("  - Check 3: Schedule references...")
        print("  - Check 4: Subsidiary legislation...")
        
        legal_context = process_context(
            key_terms=key_terms,
            pdpa_path="../data/pdpa.json",
            interpretation_path="../data/interpretation.json", 
            schedule_path="../data/schedule.json",
            subsidiary_path="../data/subsidiary.json"
        )
        
        if "No relevant categories found" in legal_context:
            result = {
                "query": user_query,
                "analysis": "No relevant PDPA provisions found for this query.",
                "status": "no_matches"
            }
            if save_output:
                save_to_output_json("No relevant PDPA provisions found for this query.")
            return result
            
        print("✓ Legal context compiled successfully")
        
        # PRINT FULL APPENDED CONTEXT FOR VERIFICATION
        print("\n" + "="*80)
        print("📚 FULL APPENDED LEGAL CONTEXT (FOR VERIFICATION)")
        print("="*80)
        print(legal_context)
        print("="*80)
        print("END OF APPENDED CONTEXT")
        print("="*80)
        
        # Step 3: Generate legal analysis using Gemini with the context
        print("\nStep 3: Generating structured legal analysis...")
        legal_analysis = analyze_legal_scenario(user_query, legal_context)
        
        # Prepare result data
        result = {
            "query": user_query,
            "analysis": legal_analysis,
            "status": "success"
        }
        
        # Save only the analysis JSON to output.json
        if save_output:
            save_to_output_json(legal_analysis)
        
        return result
        
    except Exception as e:
        error_result = {
            "query": user_query,
            "error": str(e),
            "status": "error"
        }
        if save_output:
            save_to_output_json(f'{{"error": "{str(e)}"}}')
        raise e

def main():
    """Main function to process legal queries"""
    print("="*80)
    print("SINGAPORE PDPA LEGAL ANALYSIS SYSTEM")
    print("="*80)
    print("All results will be saved to output.json")
    print()
    
    # Check if API key is configured
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your Gemini API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    while True:
        print("\nEnter your legal scenario (or 'quit' to exit):")
        print("-" * 50)
        
        # Get user input
        user_query = input("> ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for using the PDPA Legal Analysis System!")
            print("All results have been saved to output.json")
            break
            
        if not user_query:
            print("Please enter a valid legal scenario.")
            continue
            
        print("\n🔍 Processing your query...")
        print("=" * 50)
        
        try:
            result = process_query(user_query)
            
            # Display results
            print("\n" + "="*80)
            print("RELEVANT PDPA PROVISIONS")
            print("="*80)
            print()
            print("📋 QUERY:")
            print(f"{user_query}")
            print()
            print("⚖️ ANALYSIS:")
            print(result["analysis"])
            print()
            print("="*80)
            
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            print("Please try again with a different query.")
            import traceback
            traceback.print_exc()
        
        # Ask if user wants to continue
        print("\nWould you like to analyze another legal scenario? (y/n)")
        continue_choice = input("> ").strip().lower()
        if continue_choice not in ['y', 'yes']:
            print("\nThank you for using the PDPA Legal Analysis System!")
            print("All results have been saved to output.json")
            break

def test_with_sample_query():
    """Test function with the sample query provided"""
    sample_query = "An employee asks her former employer for a copy of all personal data held about her, including performance appraisals. Must her employee disclose the requested data to her? If so, how?"
    
    print("="*80)
    print("TESTING WITH SAMPLE QUERY")
    print("="*80)
    print(f"Query: {sample_query}")
    print("Results will be saved to output.json")
    
    try:
        result = process_query(sample_query)
        
        print("\n" + "="*80)
        print("SAMPLE ANALYSIS RESULT")
        print("="*80)
        print("📋 QUERY:")
        print(f"{sample_query}")
        print()
        print("⚖️ ANALYSIS:")
        print(result["analysis"])
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test with sample query first
    # test_with_sample_query()
    
    # print("\n" + "="*80)
    # print("TEST COMPLETED - Starting interactive system...")
    # print("="*80)
    
    # Run the main interactive system
    main()