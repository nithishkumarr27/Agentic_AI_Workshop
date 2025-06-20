RAG_CORPUS = [
    # ✅ General Programming Misconceptions
    "Misconception: Variable scope confusion. Learners often think variables declared inside loops or conditionals are accessible outside those blocks.",
    "Misunderstanding: Equality vs identity. Confusion between '==' and 'is' operators in Python.",
    "Misconception: Assignment vs comparison. Learners often mix up '=' and '==' in conditional statements.",
    "Misconception: Data types are interchangeable. Learners assume you can add strings and integers directly without conversion.",
    "Concept: Recursion base case. Many learners forget to define termination conditions, leading to infinite recursion.",
    "Misconception: Copying lists. Using '=' instead of `.copy()` causes shared references, leading to bugs.",
    "Misunderstanding: Logical operator precedence. Learners often group `and`, `or`, `not` incorrectly.",
    "Misconception: Variable shadowing. Learners accidentally redefine variables in inner scopes.",
    "Misconception: Loop indexing off-by-one errors. Mistakes in loop boundaries lead to missed or extra iterations.",
    "Misunderstanding: Pass-by-value vs pass-by-reference. Especially common in Python function arguments.",
    
    # ✅ Object-Oriented Programming (OOP)
    "Misconception: 'self' in Python. Learners forget to include 'self' as the first argument in instance methods.",
    "Misunderstanding: Inheritance vs composition. Learners misuse inheritance for code reuse instead of modeling relationships.",
    "Misunderstanding: Constructors don't return objects. Learners expect constructors to return values explicitly.",
    "Antipattern: Deep inheritance trees. Leads to rigid and unmaintainable class structures.",
    "Concept: Encapsulation. Learners often expose internal state instead of using getter/setter methods.",
    
    # ✅ Asynchronous Programming & Concurrency
    "Misconception: Async functions execute in parallel by default. Learners don’t understand event loop mechanics.",
    "Misunderstanding: Not awaiting async calls causes unexpected behavior or silent failures.",
    "Misconception: Threads share memory automatically. Learners don’t realize synchronization is required.",
    "Concept: Race conditions. Learners don’t account for shared state being accessed concurrently.",
    "Pattern: Use of async/await over callback chains to avoid 'callback hell'.",
    
    # ✅ Data Structures & Algorithms
    "Misunderstanding: Hash table collisions. Learners think keys must be unique values.",
    "Misconception: Binary search always works. Learners forget it requires sorted input.",
    "Concept: Recursion depth limits. Learners hit RecursionError without understanding stack growth.",
    "Pattern: Choosing appropriate data structures. Learners misuse lists where sets or dictionaries are more efficient.",
    "Antipattern: Sorting already sorted data without checking its state.",
    
    # ✅ Web Development
    "Misunderstanding: GET vs POST methods. Learners misuse HTTP methods for actions with side effects.",
    "Misconception: Frontend and backend validation are redundant. Learners remove server-side validation.",
    "Antipattern: Hardcoding URLs or credentials directly in frontend code.",
    "Pattern: Use of RESTful route structure and meaningful HTTP status codes.",
    "Concept: Same-Origin Policy and the need for CORS in frontend-backend interaction.",
    
    # ✅ Database & Querying
    "Misunderstanding: SQL injection risk. Learners build queries using raw string interpolation.",
    "Concept: Indexes speed up queries. Learners often miss adding indexes to large tables.",
    "Pattern: Use parameterized queries to prevent SQL injection.",
    "Antipattern: SELECT * usage in production code. It leads to inefficiency and fragility.",
    "Misconception: Transactions are optional. Learners forget to use commit or rollback.",
    
    # ✅ Testing & Debugging
    "Concept: Unit vs integration tests. Learners conflate their purposes and scopes.",
    "Misunderstanding: Code coverage is not equal to test quality.",
    "Antipattern: Silencing exceptions in tests instead of investigating root cause.",
    "Pattern: Using descriptive test names and meaningful assert messages.",
    "Misconception: One test per function is enough. Learners don’t account for edge cases.",
    
    # ✅ Software Engineering Practices
    "Concept: DRY principle. Learners repeat logic instead of refactoring to functions.",
    "Antipattern: God Object — one class doing too many unrelated things.",
    "Misconception: Comments should explain *what* the code does instead of *why*.",
    "Pattern: Writing clean, self-documenting code reduces the need for comments.",
    "Misunderstanding: Version control is optional. Learners don’t commit frequently or understand branching.",
    
    # ✅ Security & API Design
    "Misunderstanding: API keys are secure in frontend apps. Learners expose secrets in JavaScript code.",
    "Pattern: Validating input on both client and server sides.",
    "Misconception: HTTPS is optional for development. Learners test sensitive data over plain HTTP.",
    "Concept: Principle of Least Privilege in API key scopes and DB access.",
    "Antipattern: Returning detailed error stack traces in production APIs.",
    
    # ✅ AI/ML Programming
    "Misconception: Overfitting is good because accuracy is high. Learners don’t check validation metrics.",
    "Concept: Data leakage. Learners accidentally train models on future or leaked data.",
    "Pattern: Separating preprocessing logic for train/test to avoid leakage.",
    "Misunderstanding: Softmax output = confidence. Learners don’t consider class imbalance."
]
