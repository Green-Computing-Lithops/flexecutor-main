#!/usr/bin/env python3
"""
Script to generate 10 times more data for the Titanic dataset while maintaining the same structure.
"""

import csv
import random
import string
from datetime import datetime

# Read the original data first
def read_original_data(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Generate synthetic data based on patterns from original data
def generate_synthetic_passenger(passenger_id, original_data):
    # Sample from original data to maintain realistic distributions
    sample = random.choice(original_data)
    
    # Generate names based on patterns
    male_first_names = ['William', 'John', 'James', 'Charles', 'George', 'Frank', 'Thomas', 'Henry', 'Robert', 'Edward', 
                       'Daniel', 'Michael', 'Patrick', 'Samuel', 'David', 'Owen', 'Timothy', 'Lawrence', 'Joseph', 'Karl']
    female_first_names = ['Mary', 'Elizabeth', 'Margaret', 'Catherine', 'Helen', 'Anna', 'Ellen', 'Marie', 'Florence', 'Lily',
                          'Emma', 'Sarah', 'Alice', 'Emily', 'Grace', 'Rose', 'Clara', 'Agnes', 'Bertha', 'Gertrude']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                  'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson']
    
    # Determine sex with realistic distribution (similar to original)
    sex = random.choices(['male', 'female'], weights=[60, 40])[0]
    
    # Generate realistic age with appropriate distribution
    age_options = [None] + list(range(1, 81))
    age_weights = [5] + [1 if i < 10 else 3 if i < 30 else 2 if i < 60 else 1 for i in range(1, 81)]
    age = random.choices(age_options, weights=age_weights)[0]
    
    # Generate name based on sex
    if sex == 'male':
        first_name = random.choice(male_first_names)
        titles = ['Mr.', 'Master.'] if age and age < 16 else ['Mr.']
        title = random.choice(titles)
    else:
        first_name = random.choice(female_first_names)
        titles = ['Miss.', 'Mrs.']
        title = random.choice(titles)
    
    last_name = random.choice(last_names)
    name = f'"{last_name}, {title} {first_name}"'
    
    # Generate class with realistic distribution
    pclass = random.choices([1, 2, 3], weights=[20, 25, 55])[0]
    
    # Generate survival based on realistic factors (class, sex, age)
    survival_prob = 0.3  # base probability
    if sex == 'female':
        survival_prob += 0.4
    if pclass == 1:
        survival_prob += 0.3
    elif pclass == 2:
        survival_prob += 0.15
    if age and age < 16:
        survival_prob += 0.2
    
    survived = 1 if random.random() < min(survival_prob, 0.9) else 0
    
    # Generate family relationships
    sibsp = random.choices([0, 1, 2, 3, 4, 5], weights=[60, 25, 10, 3, 1, 1])[0]
    parch = random.choices([0, 1, 2, 3, 4, 5], weights=[70, 15, 10, 3, 1, 1])[0]
    
    # Generate ticket number
    ticket_patterns = ['A/5', 'PC', 'STON/O', 'SC/Paris', 'C.A.', 'SOTON/OQ', 'W./C.']
    if random.random() < 0.7:
        ticket = f"{random.choice(ticket_patterns)} {random.randint(10000, 99999)}"
    else:
        ticket = str(random.randint(100000, 999999))
    
    # Generate fare based on class
    if pclass == 1:
        fare = round(random.uniform(25.0, 300.0), 4)
    elif pclass == 2:
        fare = round(random.uniform(10.0, 50.0), 4)
    else:
        fare = round(random.uniform(3.0, 25.0), 4)
    
    # Generate cabin (mostly empty, some based on class)
    cabin = ''
    if pclass == 1 and random.random() < 0.6:
        cabin = f"{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 200)}"
    elif pclass == 2 and random.random() < 0.3:
        cabin = f"{random.choice(['D', 'E', 'F'])}{random.randint(1, 200)}"
    elif pclass == 3 and random.random() < 0.1:
        cabin = f"{random.choice(['F', 'G'])}{random.randint(1, 200)}"
    
    # Generate embarkation port
    embarked = random.choices(['S', 'C', 'Q'], weights=[70, 20, 10])[0]
    
    return {
        'PassengerId': passenger_id,
        'Survived': survived,
        'Pclass': pclass,
        'Name': name,
        'Sex': sex,
        'Age': age if age is not None else '',
        'SibSp': sibsp,
        'Parch': parch,
        'Ticket': ticket,
        'Fare': fare,
        'Cabin': cabin,
        'Embarked': embarked
    }

def main():
    original_file = '/home/users/iarriazu/flexecutor-main/test-bucket/titanic/titanic.csv'
    
    # Read original data
    print("Reading original data...")
    original_data = read_original_data(original_file)
    original_count = len(original_data)
    print(f"Original data has {original_count} passengers")
    
    # Calculate how many new passengers to generate (9 times the original to make 10x total)
    new_passengers_count = original_count * 9
    print(f"Generating {new_passengers_count} new passengers...")
    
    # Generate new data
    new_data = []
    starting_id = original_count + 1
    
    for i in range(new_passengers_count):
        passenger_id = starting_id + i
        new_passenger = generate_synthetic_passenger(passenger_id, original_data)
        new_data.append(new_passenger)
        
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1} passengers...")
    
    # Read the original file and append new data
    print("Writing expanded dataset...")
    
    # First, read all original data
    with open(original_file, 'r') as infile:
        original_content = infile.read()
    
    # Append new data
    with open(original_file, 'a', newline='') as outfile:
        fieldnames = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        for passenger in new_data:
            writer.writerow(passenger)
    
    print(f"Successfully expanded dataset from {original_count} to {original_count + new_passengers_count} passengers")
    print(f"Dataset is now 10 times larger!")

if __name__ == "__main__":
    main()
