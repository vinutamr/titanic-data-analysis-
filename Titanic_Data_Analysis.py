# ---------------------------
# Titanic Data Analysis Mini Project
# ---------------------------

# Step 1: Import libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 2: Load Titanic dataset
df = pd.read_csv('titanic.csv')   # make sure titanic.csv is in the same folder

# Step 3: Clean missing values
df['Age'].fillna(df['Age'].mean(), inplace=True)
df.drop(columns=['Cabin', 'Ticket'], inplace=True, errors='ignore')

# Step 4: Basic exploration
print("First 10 rows of the dataset:")
print(df.head(10))

print("\nColumn names:")
print(df.columns.tolist())

print("\nDataset shape (rows, columns):")
print(df.shape)

print("\nAverage Age of passengers:", df['Age'].mean())
print("Maximum Fare paid:", df['Fare'].max())

print("\nFirst 5 passengers (Name & Age):")
print(df[['Name', 'Age']].head(5))

# Step 5: Analysis
print("\nOverall survival rate:", df['Survived'].mean())

print("\nSurvival rate by gender:")
print(df.groupby('Sex')['Survived'].mean())

print("\nSurvival rate by passenger class:")
print(df.groupby('Pclass')['Survived'].mean())

print("\nAverage age by survival status:")
print(df.groupby('Survived')['Age'].mean())

# Step 6: Visualizations
sns.countplot(x='Survived', data=df)
plt.title("Survival Count")
plt.show()

sns.barplot(x='Pclass', y='Survived', data=df)
plt.title("Survival Rate by Class")
plt.show()

sns.barplot(x='Sex', y='Survived', data=df)
plt.title("Survival Rate by Gender")
plt.show()

sns.histplot(df['Age'], bins=20, kde=True)
plt.title("Age Distribution of Passengers")
plt.show()
