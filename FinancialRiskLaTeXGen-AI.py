import json
import csv
import io

def validate_input_data(data):
    """
    Validates input data against required fields and constraints.
    Returns tuple: (is_valid, error_messages)
    """
    required_fields = [
        "model_id", "investment_amount", "expected_return", "volatility", 
        "risk_free_rate", "market_index_level", "beta"
    ]
    
    constraints = {
        "investment_amount": lambda x: x > 0,
        "expected_return": lambda x: -100 <= x <= 100,
        "volatility": lambda x: 0 <= x <= 100,
        "risk_free_rate": lambda x: 0 <= x <= 100,
        "market_index_level": lambda x: x > 0,
        "beta": lambda x: 0 <= x <= 2
    }
    
    errors = []
    
    if not data:
        return False, ["ERROR: No data provided."]
    
    for i, record in enumerate(data):
        row_num = i + 1
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in record]
        if missing_fields:
            errors.append(f"ERROR: Missing required field(s): {', '.join(missing_fields)} in row {row_num}.")
            continue
            
        # Validate field types and constraints
        invalid_fields = []
        for field, constraint in constraints.items():
            if field in record:
                try:
                    value = float(record[field])
                    record[field] = value  # Convert to numeric type
                    if not constraint(value):
                        invalid_fields.append(field)
                except (ValueError, TypeError):
                    invalid_fields.append(field)
                    
        if invalid_fields:
            errors.append(f"ERROR: Invalid value for the field(s): {', '.join(invalid_fields)} in row {row_num}.")
    
    return len(errors) == 0, errors

def perform_calculations(record):
    """
    Performs all required risk calculations with detailed steps.
    Returns dict of calculation results.
    """
    results = {}
    
    # Extract input values
    investment_amount = float(record["investment_amount"])
    expected_return = float(record["expected_return"])
    volatility = float(record["volatility"])
    risk_free_rate = float(record["risk_free_rate"])
    market_index_level = float(record["market_index_level"])
    beta = float(record["beta"])
    
    # Risk Index Calculation
    volatility_decimal = volatility / 100
    risk_index = investment_amount * volatility_decimal
    results["risk_index"] = round(risk_index, 2)
    
    # Beta Adjusted Volatility Calculation
    beta_adjusted_volatility = volatility * beta
    results["beta_adjusted_volatility"] = round(beta_adjusted_volatility, 2)
    
    # Composite Risk Score Calculation
    risk_index_weighted = risk_index * 0.6
    beta_adj_volatility_weighted = beta_adjusted_volatility * 0.4
    composite_risk_score = risk_index_weighted + beta_adj_volatility_weighted
    results["composite_risk_score"] = round(composite_risk_score, 2)
    
    # Sharpe Ratio Calculation
    excess_return = expected_return - risk_free_rate
    if volatility_decimal == 0:  # Avoid division by zero
        sharpe_ratio = 0
    else:
        sharpe_ratio = excess_return / volatility_decimal
    results["sharpe_ratio"] = round(sharpe_ratio, 2)
    
    # Beta Impact Score Calculation
    beta_impact_score = market_index_level * beta
    results["beta_impact_score"] = round(beta_impact_score, 2)
    
    # Value at Risk (VaR) Estimation Calculation
    base_risk = investment_amount * volatility_decimal
    var = base_risk * 1.65  # 95% confidence interval
    results["var"] = round(var, 2)
    
    # Determine risk status and recommendation
    if composite_risk_score < 50:
        results["status"] = "Low Risk"
        results["recommendation"] = "Minimal risk; standard monitoring."
    elif 50 <= composite_risk_score <= 100:
        results["status"] = "Moderate Risk"
        results["recommendation"] = "Consider risk mitigation strategies."
    else:  # composite_risk_score > 100
        results["status"] = "High Risk"
        results["recommendation"] = "Immediate action required: Rebalance portfolio."
        
    return results

def generate_model_report(record, calculations):
    """
    Generates a detailed markdown report for a single risk model.
    Returns str: Markdown report for the model
    """
    model_report = f"""
### Model: **{record["model_id"]}**

#### Input Data
- **Investment Amount:** {record["investment_amount"]}
- **Expected Return (%):** {record["expected_return"]}
- **Volatility (%):** {record["volatility"]}
- **Risk Free Rate (%):** {record["risk_free_rate"]}
- **Market Index Level:** {record["market_index_level"]}
- **Beta:** {record["beta"]}

---

#### Calculation Details

1. ### **Risk Index Calculation**
 - **Formula:**  
 $$ \\text{{Risk Index}} = \\text{{investment_amount}} \\times \\frac{{\\text{{volatility}}}}{{100}} $$
 - **Steps:**  
 1. Divide *volatility* by 100: {record["volatility"]} / 100 = {record["volatility"]/100:.2f}  
 2. Multiply the result by *investment_amount*: {record["investment_amount"]} × {record["volatility"]/100:.2f} = {calculations["risk_index"]}
 - **Result:** **{calculations["risk_index"]}**

2. ### **Beta Adjusted Volatility Calculation**
 - **Formula:**  
 $$ \\text{{Beta Adjusted Volatility}} = \\text{{volatility}} \\times \\text{{beta}} $$
 - **Steps:**  
 1. Multiply *volatility* by *beta*: {record["volatility"]} × {record["beta"]} = {calculations["beta_adjusted_volatility"]}
 - **Result:** **{calculations["beta_adjusted_volatility"]}**

3. ### **Composite Risk Score Calculation**
 - **Formula:**  
 $$ \\text{{Composite Risk Score}} = (\\text{{Risk Index}} \\times 0.6) + (\\text{{Beta Adjusted Volatility}} \\times 0.4) $$
 - **Steps:**  
 1. Multiply *Risk Index* by 0.6: {calculations["risk_index"]} × 0.6 = {round(calculations["risk_index"] * 0.6, 2)}  
 2. Multiply *Beta Adjusted Volatility* by 0.4: {calculations["beta_adjusted_volatility"]} × 0.4 = {round(calculations["beta_adjusted_volatility"] * 0.4, 2)}  
 3. Add the two results together: {round(calculations["risk_index"] * 0.6, 2)} + {round(calculations["beta_adjusted_volatility"] * 0.4, 2)} = {calculations["composite_risk_score"]}
 - **Result:** **{calculations["composite_risk_score"]}**

4. ### **Sharpe Ratio Calculation**
 - **Formula:**  
 $$ \\text{{Sharpe Ratio}} = \\frac{{\\text{{expected_return}} - \\text{{risk_free_rate}}}}{{\\frac{{\\text{{volatility}}}}{{100}}}} $$
 - **Steps:**  
 1. Subtract *risk_free_rate* from *expected_return* to calculate the excess return: {record["expected_return"]} - {record["risk_free_rate"]} = {record["expected_return"] - record["risk_free_rate"]:.2f}  
 2. Convert *volatility* to a decimal by dividing by 100: {record["volatility"]} / 100 = {record["volatility"]/100:.2f}  
 3. Divide the excess return by the decimal value of *volatility*: {record["expected_return"] - record["risk_free_rate"]:.2f} / {record["volatility"]/100:.2f} = {calculations["sharpe_ratio"]}
 - **Result:** **{calculations["sharpe_ratio"]}**

5. ### **Beta Impact Score Calculation**
 - **Formula:**  
 $$ \\text{{Beta Impact Score}} = \\text{{market_index_level}} \\times \\text{{beta}} $$
 - **Steps:**  
 1. Multiply *market_index_level* by *beta*: {record["market_index_level"]} × {record["beta"]} = {calculations["beta_impact_score"]}
 - **Result:** **{calculations["beta_impact_score"]}**

6. ### **Value at Risk (VaR) Estimation Calculation**
 - **Formula:**  
 $$ \\text{{VaR}} = \\text{{investment_amount}} \\times \\frac{{\\text{{volatility}}}}{{100}} \\times 1.65 $$
 - **Steps:**  
 1. Divide *volatility* by 100: {record["volatility"]} / 100 = {record["volatility"]/100:.2f}  
 2. Multiply the result by *investment_amount* to get the base risk: {record["investment_amount"]} × {record["volatility"]/100:.2f} = {round(record["investment_amount"] * record["volatility"]/100, 2)}  
 3. Multiply the base risk by 1.65 (confidence factor for 95% confidence interval): {round(record["investment_amount"] * record["volatility"]/100, 2)} × 1.65 = {calculations["var"]}
 - **Result:** **{calculations["var"]}**
"""
    return model_report

def generate_final_report(data, calculations_list):
    """
    Generates the complete markdown report for all risk models.
    Returns str: Complete markdown report
    """
    # Header
    report = """# Financial Risk Model Report

---

## Overview
"""
    
    # Add overview information
    report += f"- **Total Risk Models Evaluated:** **{len(data)}**\n\n---\n\n## Detailed Analysis per Model\n"
    
    # Add each model's report
    for i, (record, calculations) in enumerate(zip(data, calculations_list)):
        report += generate_model_report(record, calculations)
        
        # Add final recommendation for each model
        report += f"""
---

## Final Recommendation

- **Composite Risk Score:** **{calculations["composite_risk_score"]}**
- **Status:** **{calculations["status"]}**
- **Recommended Action:** **{calculations["recommendation"]}**
"""
        # Add separator between models if not the last one
        if i < len(data) - 1:
            report += "\n\n---\n\n"
    
    return report

def parse_csv_data(csv_text):
    """Parse CSV text into a list of dictionaries."""
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)

def parse_json_data(json_text):
    """Parse JSON text into a list of dictionaries."""
    try:
        data = json.loads(json_text)
        # Handle both direct list and "models" key format
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "models" in data:
            return data["models"]
        else:
            return []
    except json.JSONDecodeError:
        return []

def detect_and_parse_data(input_text):
    """
    Detect if input text is CSV or JSON and parse accordingly.
    Returns tuple: (data_format, parsed_data)
    """
    # Clean the input text
    input_text = input_text.strip()
    
    # Check if it looks like JSON
    if (input_text.startswith('{') and input_text.endswith('}')) or \
       (input_text.startswith('[') and input_text.endswith(']')):
        return "JSON", parse_json_data(input_text)
    
    # Check if it looks like CSV
    elif ',' in input_text and '\n' in input_text:
        return "CSV", parse_csv_data(input_text)
    
    # Can't determine format
    else:
        return "UNKNOWN", []

def process_financial_risk_model(input_data):
    """
    Process the input data and generate the financial risk report.
    Returns the generated report text
    """
    # Detect and parse input format
    data_format, data = detect_and_parse_data(input_data)
    
    if data_format == "UNKNOWN" or not data:
        return "ERROR: Invalid data format. Please provide data in CSV or JSON format."
    
    # Validate the input data (we'll still validate but not show this part)
    is_valid, errors = validate_input_data(data)
    
    if not is_valid:
        error_msg = "\n".join(errors)
        return f"ERROR: Data validation failed.\n{error_msg}"
    
    # Perform calculations for each model
    calculations_list = []
    for record in data:
        calculations = perform_calculations(record)
        calculations_list.append(calculations)
    
    # Generate the final report
    final_report = generate_final_report(data, calculations_list)
    
    return final_report

def main():
    """
    Main function with sample data demonstration.
    """
    # Sample JSON data
    sample_json_data = """
    {
        "models": [
    {
      "model_id": "JSONModel1",
      "investment_amount": 50,
      "expected_return": 2,
      "volatility": 5,
      "risk_free_rate": 1,
      "market_index_level": 500,
      "beta": 0.5
    },
    {
      "model_id": "JSONModel2",
      "investment_amount": 100,
      "expected_return": 4,
      "volatility": 8,
      "risk_free_rate": 1.5,
      "market_index_level": 800,
      "beta": 0.7
    },
    {
      "model_id": "JSONModel3",
      "investment_amount": 200,
      "expected_return": 6,
      "volatility": 15,
      "risk_free_rate": 2,
      "market_index_level": 1500,
      "beta": 0.9
    },
    {
      "model_id": "JSONModel4",
      "investment_amount": 300,
      "expected_return": 10,
      "volatility": 40,
      "risk_free_rate": 3,
      "market_index_level": 1800,
      "beta": 1.0
    },
    {
      "model_id": "JSONModel5",
      "investment_amount": 250,
      "expected_return": 8,
      "volatility": 35,
      "risk_free_rate": 2,
      "market_index_level": 1600,
      "beta": 0.8
    },
    {
      "model_id": "JSONModel6",
      "investment_amount": 120,
      "expected_return": 5,
      "volatility": 10,
      "risk_free_rate": 1.5,
      "market_index_level": 900,
      "beta": 0.6
    }
  ]
    }
    """
    report = process_financial_risk_model(sample_json_data)
    return report

if __name__ == "__main__":
    # Run the main function and print the output
    result = main()
    print(result)