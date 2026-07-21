"""
CareerAI — Careers & Learning Knowledge Base

CAREERS        : 8 career definitions (canonical skill names match
                 utils/resume_parser.py SKILL_TAXONOMY exactly).
SKILL_MODULES  : per-skill learning modules — free resources, an embeddable
                 YouTube video, and a 3-question quiz.
default_module : real, working fallback links for skills without a
                 dedicated module (bonus skills).
"""

CAREERS = [
    {
        "title": "Frontend Developer",
        "category": "Web Development",
        "description": "Build beautiful, responsive user interfaces and interactive web experiences using modern JavaScript frameworks.",
        "core_skills": ["HTML", "CSS", "JavaScript", "React", "Git"],
        "bonus_skills": ["TypeScript", "Tailwind CSS", "Redux", "Next.js"],
    },
    {
        "title": "Backend Developer",
        "category": "Web Development",
        "description": "Design and build the server-side logic, APIs, and databases that power modern applications.",
        "core_skills": ["Python", "Flask", "SQL", "REST API", "Git"],
        "bonus_skills": ["Docker", "MongoDB", "Node.js", "Redis"],
    },
    {
        "title": "Full-Stack Developer",
        "category": "Web Development",
        "description": "Own features end to end — from pixel-perfect frontends to scalable backend services and databases.",
        "core_skills": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"],
        "bonus_skills": ["MongoDB", "Docker", "TypeScript", "Git"],
    },
    {
        "title": "Data Scientist",
        "category": "Data & AI",
        "description": "Extract insights from data using statistics and machine learning to drive business decisions.",
        "core_skills": ["Python", "Statistics", "Pandas", "Machine Learning", "Data Visualization"],
        "bonus_skills": ["SQL", "Deep Learning", "NumPy", "Tableau"],
    },
    {
        "title": "Machine Learning Engineer",
        "category": "Data & AI",
        "description": "Build, train, and deploy production machine learning models and intelligent systems at scale.",
        "core_skills": ["Python", "Machine Learning", "Deep Learning", "Scikit-learn", "TensorFlow"],
        "bonus_skills": ["MLOps", "Docker", "NumPy", "Natural Language Processing"],
    },
    {
        "title": "Data Analyst",
        "category": "Data & AI",
        "description": "Turn raw data into dashboards, reports, and stories that help teams make smarter decisions.",
        "core_skills": ["Excel", "SQL", "Data Analysis", "Data Visualization", "Statistics"],
        "bonus_skills": ["Python", "Power BI", "Tableau", "Pandas"],
    },
    {
        "title": "DevOps Engineer",
        "category": "Infrastructure",
        "description": "Automate build, test, and deployment pipelines and keep production systems fast and reliable.",
        "core_skills": ["Linux", "Docker", "CI/CD", "Git", "Bash"],
        "bonus_skills": ["Kubernetes", "AWS", "Terraform", "Jenkins"],
    },
    {
        "title": "UI/UX Designer",
        "category": "Design",
        "description": "Research, wireframe, and design intuitive digital products that users love to use.",
        "core_skills": ["UI/UX Design", "Figma", "Wireframing", "Prototyping"],
        "bonus_skills": ["HTML", "CSS", "Adobe XD", "Communication"],
    },
]


CAREER_SIGNAL_PROFILE = {
    "Frontend Developer": {
        "min_experience_years": 0.0,
        "preferred_education": ["bachelor", "master", "diploma", "certification"],
    },
    "Backend Developer": {
        "min_experience_years": 0.0,
        "preferred_education": ["bachelor", "master", "diploma", "certification"],
    },
    "Full-Stack Developer": {
        "min_experience_years": 1.0,
        "preferred_education": ["bachelor", "master", "diploma", "certification"],
    },
    "Data Scientist": {
        "min_experience_years": 2.0,
        "preferred_education": ["bachelor", "master", "phd"],
    },
    "Machine Learning Engineer": {
        "min_experience_years": 3.0,
        "preferred_education": ["bachelor", "master", "phd"],
    },
    "Data Analyst": {
        "min_experience_years": 0.0,
        "preferred_education": ["bachelor", "master", "diploma", "certification"],
    },
    "DevOps Engineer": {
        "min_experience_years": 2.0,
        "preferred_education": ["bachelor", "master", "diploma", "certification"],
    },
    "UI/UX Designer": {
        "min_experience_years": 0.0,
        "preferred_education": ["bachelor", "master", "diploma", "certification"],
    },
}


ROLE_HINTS = {
    "software engineer": ["Frontend Developer", "Backend Developer", "Full-Stack Developer"],
    "web developer": ["Frontend Developer", "Full-Stack Developer"],
    "frontend developer": ["Frontend Developer"],
    "front end developer": ["Frontend Developer"],
    "backend developer": ["Backend Developer"],
    "back end developer": ["Backend Developer"],
    "full stack developer": ["Full-Stack Developer"],
    "fullstack developer": ["Full-Stack Developer"],
    "data scientist": ["Data Scientist"],
    "machine learning engineer": ["Machine Learning Engineer"],
    "ml engineer": ["Machine Learning Engineer"],
    "data analyst": ["Data Analyst"],
    "data engineer": ["Data Scientist", "Machine Learning Engineer", "Data Analyst"],
    "devops engineer": ["DevOps Engineer"],
    "site reliability engineer": ["DevOps Engineer"],
    "sre": ["DevOps Engineer"],
    "ui ux designer": ["UI/UX Designer"],
    "ux designer": ["UI/UX Designer"],
    "ui designer": ["UI/UX Designer"],
    "product designer": ["UI/UX Designer"],
}


SKILL_MODULES = {
    "HTML": {
        "weeks": 1,
        "resources": [
            {"name": "MDN — HTML Basics", "url": "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/HTML_basics", "platform": "MDN"},
            {"name": "freeCodeCamp — Responsive Web Design", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "platform": "freeCodeCamp"},
        ],
        "videos": [{"title": "HTML Full Course — Build a Website", "youtube_id": "pQN-pnXPaVg"}],
        "quiz": [
            {"q": "Which tag creates a hyperlink?", "options": ["<link>", "<a>", "<href>", "<url>"], "answer": 1},
            {"q": "Which element is the correct container for page metadata?", "options": ["<body>", "<footer>", "<head>", "<main>"], "answer": 2},
            {"q": "What does semantic HTML improve?", "options": ["File size only", "Accessibility and SEO", "CSS speed", "JavaScript execution"], "answer": 1},
            {"q": "Which tag creates the largest heading?", "options": ["<heading>", "<h1>", "<h6>", "<title>"], "answer": 1},
            {"q": "What does the alt attribute on an <img> tag provide?", "options": ["The image URL", "Text alternative for accessibility", "Image dimensions", "Caption styling"], "answer": 1},
        ],
    },
    "CSS": {
        "weeks": 1,
        "resources": [
            {"name": "MDN — CSS First Steps", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/First_steps", "platform": "MDN"},
            {"name": "CSS-Tricks — Flexbox Guide", "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/", "platform": "CSS-Tricks"},
        ],
        "videos": [{"title": "CSS Tutorial — Zero to Hero", "youtube_id": "1Rs2ND1ryYc"}],
        "quiz": [
            {"q": "Which property controls the space INSIDE an element's border?", "options": ["margin", "gap", "padding", "spacing"], "answer": 2},
            {"q": "Which display value enables Flexbox?", "options": ["display: grid", "display: flex", "display: block", "display: inline"], "answer": 1},
            {"q": "Which unit is relative to the root font size?", "options": ["px", "em", "rem", "vh"], "answer": 2},
            {"q": "Which property changes text color?", "options": ["font-color", "text-color", "color", "foreground"], "answer": 2},
            {"q": "What does the z-index property control?", "options": ["Zoom level", "Stacking order of elements", "Font weight", "Border thickness"], "answer": 1},
        ],
    },
    "JavaScript": {
        "weeks": 3,
        "resources": [
            {"name": "MDN — JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "platform": "MDN"},
            {"name": "javascript.info — The Modern JS Tutorial", "url": "https://javascript.info/", "platform": "javascript.info"},
        ],
        "videos": [{"title": "Learn JavaScript — Full Course for Beginners", "youtube_id": "PkZNo7MFNFg"}],
        "quiz": [
            {"q": "Which keyword declares a block-scoped variable that can be reassigned?", "options": ["var", "let", "const", "static"], "answer": 1},
            {"q": "What does === check that == does not?", "options": ["Value only", "Reference", "Type as well as value", "Nothing extra"], "answer": 2},
            {"q": "Which method turns a JSON string into an object?", "options": ["JSON.stringify()", "JSON.parse()", "JSON.object()", "JSON.decode()"], "answer": 1},
            {"q": "What is the result of typeof []?", "options": ["array", "object", "list", "undefined"], "answer": 1},
            {"q": "Which function schedules code to run after a delay?", "options": ["setInterval()", "setTimeout()", "delay()", "wait()"], "answer": 1},
        ],
    },
    "React": {
        "weeks": 3,
        "resources": [
            {"name": "React — Official Learn Course", "url": "https://react.dev/learn", "platform": "react.dev"},
            {"name": "freeCodeCamp — Front End Libraries", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "platform": "freeCodeCamp"},
        ],
        "videos": [{"title": "React Course — Beginner's Tutorial", "youtube_id": "bMknfKXIFA8"}],
        "quiz": [
            {"q": "Which hook stores local component state?", "options": ["useEffect", "useState", "useRef", "useMemo"], "answer": 1},
            {"q": "What is JSX?", "options": ["A CSS preprocessor", "A syntax extension for writing UI in JS", "A database query language", "A build tool"], "answer": 1},
            {"q": "How does data usually flow in React?", "options": ["Child to parent", "Parent to child via props", "Randomly", "Through global variables"], "answer": 1},
            {"q": "Which hook runs side effects in a component?", "options": ["useState", "useEffect", "useContext", "useReducer"], "answer": 1},
            {"q": "What is the virtual DOM?", "options": ["A browser API", "A lightweight copy of the real DOM for efficient updates", "A CSS framework", "A database"], "answer": 1},
        ],
    },
    "Git": {
        "weeks": 1,
        "resources": [
            {"name": "Git — Official Book (free)", "url": "https://git-scm.com/book/en/v2", "platform": "git-scm.com"},
            {"name": "GitHub — Hello World Guide", "url": "https://docs.github.com/en/get-started/start-your-journey/hello-world", "platform": "GitHub Docs"},
        ],
        "videos": [{"title": "Git and GitHub for Beginners — Crash Course", "youtube_id": "RGOj5yH7evk"}],
        "quiz": [
            {"q": "Which command records staged changes?", "options": ["git push", "git commit", "git add", "git save"], "answer": 1},
            {"q": "Which command creates and switches to a new branch?", "options": ["git branch -m", "git checkout -b", "git merge", "git switch --delete"], "answer": 1},
            {"q": "What does git pull do?", "options": ["Deletes a branch", "Fetches and merges remote changes", "Uploads commits", "Creates a repository"], "answer": 1},
            {"q": "Which command shows the commit history?", "options": ["git status", "git log", "git diff", "git show"], "answer": 1},
            {"q": "What does git clone do?", "options": ["Deletes a repository", "Copies a remote repository locally", "Merges branches", "Creates a tag"], "answer": 1},
        ],
    },
    "Python": {
        "weeks": 3,
        "resources": [
            {"name": "Python — Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "platform": "python.org"},
            {"name": "freeCodeCamp — Scientific Computing with Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "platform": "freeCodeCamp"},
        ],
        "videos": [{"title": "Learn Python — Full Course for Beginners", "youtube_id": "rfscVS0vtbw"}],
        "quiz": [
            {"q": "Which data type is immutable?", "options": ["list", "dict", "tuple", "set"], "answer": 2},
            {"q": "What does a list comprehension produce?", "options": ["A generator only", "A new list", "A dictionary", "A string"], "answer": 1},
            {"q": "Which keyword defines a function?", "options": ["func", "lambda only", "def", "define"], "answer": 2},
            {"q": "What does the len() function return?", "options": ["The type of an object", "The number of items in a container", "The memory address", "The last element"], "answer": 1},
            {"q": "Which statement handles exceptions?", "options": ["catch/throw", "try/except", "error/handle", "if/else"], "answer": 1},
        ],
    },
    "Flask": {
        "weeks": 2,
        "resources": [
            {"name": "Flask — Official Quickstart", "url": "https://flask.palletsprojects.com/en/stable/quickstart/", "platform": "Flask Docs"},
            {"name": "Miguel Grinberg — Flask Mega-Tutorial", "url": "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world", "platform": "Blog"},
        ],
        "videos": [{"title": "Flask Course — Python Web Development", "youtube_id": "Z1RJmh_OqeA"}],
        "quiz": [
            {"q": "What decorator maps a URL to a function?", "options": ["@app.get_url", "@app.route", "@flask.path", "@app.map"], "answer": 1},
            {"q": "What are Flask Blueprints used for?", "options": ["Database models", "Organizing routes into modules", "CSS templating", "Testing only"], "answer": 1},
            {"q": "Which object holds incoming form/JSON data?", "options": ["flask.data", "app.input", "request", "response"], "answer": 2},
            {"q": "Which function renders an HTML template?", "options": ["send_file", "render_template", "redirect", "template_load"], "answer": 1},
            {"q": "What is Flask default template engine?", "options": ["React", "Jinja2", "Django", "Handlebars"], "answer": 1},
        ],
    },
    "SQL": {
        "weeks": 2,
        "resources": [
            {"name": "SQLBolt — Interactive SQL Lessons", "url": "https://sqlbolt.com/", "platform": "SQLBolt"},
            {"name": "Kaggle — Intro to SQL", "url": "https://www.kaggle.com/learn/intro-to-sql", "platform": "Kaggle Learn"},
        ],
        "videos": [{"title": "SQL Tutorial — Full Database Course", "youtube_id": "HXV3zeQKqGY"}],
        "quiz": [
            {"q": "Which clause filters rows?", "options": ["ORDER BY", "WHERE", "GROUP BY", "SELECT"], "answer": 1},
            {"q": "Which JOIN returns only matching rows from both tables?", "options": ["LEFT JOIN", "FULL JOIN", "INNER JOIN", "CROSS JOIN"], "answer": 2},
            {"q": "What does a PRIMARY KEY guarantee?", "options": ["Fast deletes", "Unique, non-null row identity", "Sorted storage", "Encrypted data"], "answer": 1},
            {"q": "Which clause groups rows with aggregate functions?", "options": ["ORDER BY", "GROUP BY", "HAVING", "LIMIT"], "answer": 1},
            {"q": "What does the AVG function return?", "options": ["Sum of values", "Average of numeric values", "Count of rows", "Maximum value"], "answer": 1},
        ],
    },
    "REST API": {
        "weeks": 1,
        "resources": [
            {"name": "MDN — HTTP Overview", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", "platform": "MDN"},
            {"name": "freeCodeCamp — REST API Best Practices", "url": "https://www.freecodecamp.org/news/rest-api-best-practices-rest-endpoint-design-examples/", "platform": "freeCodeCamp"},
        ],
        "videos": [{"title": "APIs for Beginners — How to Use an API", "youtube_id": "GZvSYJDk-us"}],
        "quiz": [
            {"q": "Which HTTP method is used to create a resource?", "options": ["GET", "POST", "DELETE", "HEAD"], "answer": 1},
            {"q": "What does status code 404 mean?", "options": ["Server error", "Unauthorized", "Not found", "Created"], "answer": 2},
{"q": "Which format do most REST APIs exchange?", "options": ["CSV", "JSON", "YAML", "Binary"], "answer": 1},
            {"q": "Which HTTP method is idempotent and updates a resource?", "options": ["POST", "PUT", "PATCH", "DELETE"], "answer": 1},
            {"q": "Status code 201 indicates?", "options": ["OK", "Created successfully", "No Content", "Bad Request"], "answer": 1},
        ],
    },
    "Node.js": {
        "weeks": 2,
        "resources": [
            {"name": "Node.js — Official Learn Guides", "url": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs", "platform": "nodejs.org"},
            {"name": "freeCodeCamp — Back End APIs", "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/", "platform": "freeCodeCamp"},
        ],
        "videos": [{"title": "Node.js and Express.js — Full Course", "youtube_id": "Oe421EPjeBE"}],
        "quiz": [
            {"q": "Node.js runs JavaScript on the…", "options": ["Browser only", "Server", "Database", "GPU"], "answer": 1},
            {"q": "Which file lists a project's dependencies?", "options": ["node.config", "package.json", "deps.txt", "modules.js"], "answer": 1},
{"q": "Which keyword handles a promise's resolved value inside an async function?", "options": ["yield", "await", "then only", "defer"], "answer": 1},
            {"q": "Which module handles file system operations?", "options": ["http", "path", "fs", "url"], "answer": 2},
            {"q": "What does npm do?", "options": ["Runs JavaScript", "Manages packages", "Compiles TypeScript", "Handles CSS"], "answer": 1},
        ],
    },
    "Statistics": {
        "weeks": 2,
        "resources": [
            {"name": "Khan Academy — Statistics & Probability", "url": "https://www.khanacademy.org/math/statistics-probability", "platform": "Khan Academy"},
            {"name": "OpenIntro Statistics (free book)", "url": "https://www.openintro.org/book/os/", "platform": "OpenIntro"},
        ],
        "videos": [{"title": "Statistics — Full University Course", "youtube_id": "xxpc-HPKN28"}],
        "quiz": [
            {"q": "Which measure is most affected by outliers?", "options": ["Median", "Mode", "Mean", "IQR"], "answer": 2},
            {"q": "A p-value below 0.05 typically indicates…", "options": ["Proof of causation", "Statistical significance", "A sampling error", "A perfect model"], "answer": 1},
{"q": "Standard deviation measures…", "options": ["Central tendency", "Spread of data", "Sample size", "Correlation"], "answer": 1},
            {"q": "Which distribution is symmetric and bell-shaped?", "options": ["Poisson", "Normal", "Exponential", "Uniform"], "answer": 1},
            {"q": "What does a confidence interval estimate?", "options": ["Exact population value", "A range likely containing the true parameter", "The sample size", "The p-value"], "answer": 1},
        ],
    },
    "Pandas": {
        "weeks": 2,
        "resources": [
            {"name": "Pandas — Official 10 Minutes Guide", "url": "https://pandas.pydata.org/docs/user_guide/10min.html", "platform": "pandas.pydata.org"},
            {"name": "Kaggle — Pandas Course", "url": "https://www.kaggle.com/learn/pandas", "platform": "Kaggle Learn"},
        ],
        "videos": [{"title": "Data Analysis with Python — Pandas", "youtube_id": "vmEHCJofslg"}],
        "quiz": [
            {"q": "Which object represents a 2-D labeled table?", "options": ["Series", "DataFrame", "Array", "Matrix"], "answer": 1},
            {"q": "Which method selects rows by label?", "options": [".iloc[]", ".loc[]", ".get()", ".rows[]"], "answer": 1},
{"q": "Which function reads a CSV file?", "options": ["pd.open_csv()", "pd.read_csv()", "pd.load()", "pd.csv()"], "answer": 1},
            {"q": "What does df.groupby() do?", "options": ["Deletes rows", "Groups data by a column for aggregation", "Sorts the dataframe", "Merges two dataframes"], "answer": 1},
            {"q": "Which method fills missing values?", "options": ["df.clean()", "df.fillna()", "df.remove_na()", "df.drop_null()"], "answer": 1},
        ],
    },
    "Machine Learning": {
        "weeks": 4,
        "resources": [
            {"name": "Google — Machine Learning Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "platform": "Google"},
            {"name": "Kaggle — Intro to Machine Learning", "url": "https://www.kaggle.com/learn/intro-to-machine-learning", "platform": "Kaggle Learn"},
        ],
        "videos": [{"title": "Machine Learning for Everybody", "youtube_id": "NWONeJKn6kc"}],
        "quiz": [
            {"q": "Predicting a continuous value is called…", "options": ["Classification", "Regression", "Clustering", "Reduction"], "answer": 1},
            {"q": "Overfitting means a model…", "options": ["Trains too slowly", "Memorizes training data and generalizes poorly", "Has too few features", "Underestimates all values"], "answer": 1},
            {"q": "Which dataset split evaluates final performance?", "options": ["Training set", "Validation set", "Test set", "Full dataset"], "answer": 2},
            {"q": "What is a hyperparameter?", "options": ["A learned weight", "A setting configured before training", "An output label", "A data type"], "answer": 1},
            {"q": "Random Forest is an example of...", "options": ["Unsupervised learning", "An ensemble method", "Linear regression", "Dimensionality reduction"], "answer": 1},
        ],
    },
    "Data Visualization": {
        "weeks": 1,
        "resources": [
            {"name": "Kaggle — Data Visualization Course", "url": "https://www.kaggle.com/learn/data-visualization", "platform": "Kaggle Learn"},
            {"name": "Matplotlib — Official Tutorials", "url": "https://matplotlib.org/stable/tutorials/index.html", "platform": "matplotlib.org"},
        ],
        "videos": [{"title": "Matplotlib Crash Course", "youtube_id": "3Xc3CA655Y4"}],
        "quiz": [
            {"q": "Which chart best shows a trend over time?", "options": ["Pie chart", "Line chart", "Histogram", "Box plot"], "answer": 1},
            {"q": "A histogram displays…", "options": ["Category proportions", "Distribution of a numeric variable", "Correlation", "Geospatial data"], "answer": 1},
            {"q": "Which library is built on top of Matplotlib for statistical plots?", "options": ["NumPy", "Seaborn", "Flask", "Requests"], "answer": 1},
            {"q": "Which chart best compares proportions of a whole?", "options": ["Scatter plot", "Pie chart", "Line chart", "Bar chart"], "answer": 1},
            {"q": "What does a box plot show?", "options": ["Time series", "Distribution summary with quartiles", "Correlation", "Raw data points"], "answer": 1},
        ],
    },
    "Deep Learning": {
        "weeks": 4,
        "resources": [
            {"name": "3Blue1Brown — Neural Networks Series", "url": "https://www.3blue1brown.com/topics/neural-networks", "platform": "3Blue1Brown"},
            {"name": "fast.ai — Practical Deep Learning (free)", "url": "https://course.fast.ai/", "platform": "fast.ai"},
        ],
        "videos": [{"title": "Deep Learning Crash Course for Beginners", "youtube_id": "VyWAvY2CF9c"}],
        "quiz": [
            {"q": "Which function introduces non-linearity in a network?", "options": ["Loss function", "Activation function", "Optimizer", "Regularizer"], "answer": 1},
            {"q": "Backpropagation is used to…", "options": ["Load data", "Compute gradients and update weights", "Normalize inputs", "Split datasets"], "answer": 1},
            {"q": "CNNs are especially effective for…", "options": ["Tabular data", "Image data", "SQL queries", "Text encryption"], "answer": 1},
            {"q": "What is dropout used for?", "options": ["Speeding up training", "Preventing overfitting by randomly disabling neurons", "Increasing model size", "Normalizing inputs"], "answer": 1},
            {"q": "RNNs are designed to handle…", "options": ["Image data only", "Sequential data like text and time series", "Tabular data", "Audio only"], "answer": 1},
        ],
    },
    "Scikit-learn": {
        "weeks": 2,
        "resources": [
            {"name": "Scikit-learn — Getting Started", "url": "https://scikit-learn.org/stable/getting_started.html", "platform": "scikit-learn.org"},
            {"name": "Kaggle — Intermediate Machine Learning", "url": "https://www.kaggle.com/learn/intermediate-machine-learning", "platform": "Kaggle Learn"},
        ],
        "videos": [{"title": "Scikit-learn Crash Course", "youtube_id": "0B5eIE_1vpU"}],
        "quiz": [
            {"q": "Which method trains a scikit-learn model?", "options": [".train()", ".fit()", ".learn()", ".run()"], "answer": 1},
            {"q": "train_test_split is used to…", "options": ["Scale features", "Split data for evaluation", "Tune hyperparameters", "Encode labels"], "answer": 1},
            {"q": "Which object chains preprocessing and a model together?", "options": ["GridSearchCV", "Pipeline", "ColumnStack", "Estimator"], "answer": 1},
            {"q": "Which method makes predictions on new data?", "options": [".predict()", ".transform()", ".score()", ".fit()"], "answer": 0},
            {"q": "What does cross_val_score evaluate?", "options": ["Training speed", "Model performance across multiple folds", "Memory usage", "Feature importance"], "answer": 1},
        ],
    },
    "TensorFlow": {
        "weeks": 3,
        "resources": [
            {"name": "TensorFlow — Official Tutorials", "url": "https://www.tensorflow.org/tutorials", "platform": "tensorflow.org"},
            {"name": "Keras — Getting Started Guides", "url": "https://keras.io/getting_started/", "platform": "keras.io"},
        ],
        "videos": [{"title": "TensorFlow 2.0 Complete Course", "youtube_id": "tPYj3fFJGjk"}],
        "quiz": [
            {"q": "The core data structure in TensorFlow is the…", "options": ["DataFrame", "Tensor", "Array list", "Graph node"], "answer": 1},
            {"q": "Keras is…", "options": ["A database", "TensorFlow's high-level model API", "A GPU driver", "A visualization tool"], "answer": 1},
            {"q": "model.compile() configures…", "options": ["The dataset", "Loss, optimizer, and metrics", "The GPU", "Layer weights directly"], "answer": 1},
            {"q": "What is a GradientTape used for?", "options": ["Data loading", "Recording operations for automatic differentiation", "Visualizing graphs", "Saving models"], "answer": 1},
            {"q": "Which API style is tf.keras considered?", "options": ["Low-level only", "High-level and user-friendly", "Functional only", "Legacy"], "answer": 1},
        ],
    },
    "Excel": {
        "weeks": 1,
        "resources": [
            {"name": "Microsoft — Excel Training Center", "url": "https://support.microsoft.com/en-us/office/excel-video-training-9bc05390-e94c-46af-a5b3-d7c22f6990bb", "platform": "Microsoft"},
            {"name": "Excel Easy — Free Tutorial", "url": "https://www.excel-easy.com/", "platform": "Excel Easy"},
        ],
        "videos": [{"title": "Excel Tutorial for Beginners", "youtube_id": "Vl0H-qTclOg"}],
        "quiz": [
            {"q": "Which function looks up a value in the first column of a range?", "options": ["INDEX", "VLOOKUP", "SUMIF", "MATCH only"], "answer": 1},
            {"q": "A PivotTable is used to…", "options": ["Draw shapes", "Summarize and aggregate data", "Write macros", "Format cells"], "answer": 1},
            {"q": "What does $A$1 mean in a formula?", "options": ["Currency cell", "Absolute reference", "Named range", "Error value"], "answer": 1},
            {"q": "Conditional formatting changes cell appearance based on…", "options": ["Cell address", "Cell values or formulas", "Font size", "Print settings"], "answer": 1},
            {"q": "What does Freeze Panes do?", "options": ["Hides rows", "Keeps rows or columns visible while scrolling", "Locks cells from editing", "Deletes data"], "answer": 1},
        ],
    },
    "Data Analysis": {
        "weeks": 2,
        "resources": [
            {"name": "freeCodeCamp — Data Analysis with Python", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "platform": "freeCodeCamp"},
            {"name": "Kaggle — Learn Platform", "url": "https://www.kaggle.com/learn", "platform": "Kaggle Learn"},
        ],
        "videos": [{"title": "Data Analysis with Python — Full Course", "youtube_id": "r-uOLxNrNk8"}],
        "quiz": [
            {"q": "The first step in most data analysis projects is…", "options": ["Modeling", "Data cleaning and exploration", "Deployment", "Reporting"], "answer": 1},
            {"q": "Missing values in a dataset can be handled by…", "options": ["Ignoring the whole project", "Imputation or removal", "Duplicating rows", "Encrypting them"], "answer": 1},
            {"q": "EDA stands for…", "options": ["Extra Data Allocation", "Exploratory Data Analysis", "Encoded Data Array", "External Database Access"], "answer": 1},
            {"q": "A correlation matrix shows…", "options": ["Row counts", "Pairwise correlations between variables", "Data types", "File sizes"], "answer": 1},
            {"q": "Outlier detection helps identify…", "options": ["Normal data points", "Anomalous or extreme values", "Missing values", "Duplicate records"], "answer": 1},
        ],
    },
    "Linux": {
        "weeks": 2,
        "resources": [
            {"name": "Linux Journey — Free Lessons", "url": "https://linuxjourney.com/", "platform": "Linux Journey"},
            {"name": "Ubuntu — Command Line for Beginners", "url": "https://ubuntu.com/tutorials/command-line-for-beginners", "platform": "Ubuntu"},
        ],
        "videos": [{"title": "Linux Operating System — Crash Course", "youtube_id": "ROjZy1WbCIA"}],
        "quiz": [
            {"q": "Which command lists directory contents?", "options": ["cd", "ls", "pwd", "cat"], "answer": 1},
            {"q": "Which command changes file permissions?", "options": ["chown", "chmod", "perm", "sudo"], "answer": 1},
            {"q": "The root user's home directory is…", "options": ["/home/root", "/root", "/usr/root", "/admin"], "answer": 1},
            {"q": "Which command finds text inside files?", "options": ["find", "grep", "locate", "search"], "answer": 1},
            {"q": "What does the pipe operator do?", "options": ["Runs commands in parallel", "Sends output of one command as input to another", "Deletes files", "Copies files"], "answer": 1},
        ],
    },
    "Docker": {
        "weeks": 2,
        "resources": [
            {"name": "Docker — Official Get Started", "url": "https://docs.docker.com/get-started/", "platform": "Docker Docs"},
            {"name": "Play with Docker — Free Labs", "url": "https://labs.play-with-docker.com/", "platform": "Docker"},
        ],
        "videos": [{"title": "Docker Tutorial for Beginners — Full Course", "youtube_id": "fqMOX6JJhGo"}],
        "quiz": [
            {"q": "A Docker image is…", "options": ["A running process", "A read-only template for containers", "A virtual machine", "A network"], "answer": 1},
            {"q": "Which file defines how an image is built?", "options": ["docker.yml", "Dockerfile", "image.conf", "build.json"], "answer": 1},
            {"q": "Which command runs a container?", "options": ["docker start-image", "docker run", "docker exec-new", "docker boot"], "answer": 1},
            {"q": "A Docker container is…", "options": ["A full virtual machine", "An isolated running instance of an image", "A source code file", "A cloud server"], "answer": 1},
            {"q": "Which command stops a running container?", "options": ["docker kill", "docker stop", "docker remove", "docker end"], "answer": 1},
        ],
    },
    "CI/CD": {
        "weeks": 2,
        "resources": [
            {"name": "GitLab — CI/CD Documentation", "url": "https://docs.gitlab.com/ee/ci/", "platform": "GitLab Docs"},
            {"name": "GitHub Actions — Quickstart", "url": "https://docs.github.com/en/actions/writing-workflows/quickstart", "platform": "GitHub Docs"},
        ],
        "videos": [{"title": "GitLab CI/CD Tutorial for Beginners", "youtube_id": "qP8kir2GUgo"}],
        "quiz": [
            {"q": "CI stands for…", "options": ["Code Injection", "Continuous Integration", "Container Instance", "Central Index"], "answer": 1},
            {"q": "A pipeline typically runs…", "options": ["Only on release day", "On every push/merge automatically", "Once per year", "Manually only"], "answer": 1},
            {"q": "The main benefit of CD is…", "options": ["Bigger releases", "Frequent, reliable automated deployments", "Fewer tests", "Manual approvals everywhere"], "answer": 1},
            {"q": "Which tool automates CI/CD on GitHub?", "options": ["Jira", "GitHub Actions", "Slack", "Docker Compose"], "answer": 1},
            {"q": "What is a CI/CD webhook trigger?", "options": ["A manual button", "An automatic event that starts a pipeline on code changes", "A database query", "A file upload"], "answer": 1},
        ],
    },
    "Bash": {
        "weeks": 1,
        "resources": [
            {"name": "GNU — Bash Reference Manual", "url": "https://www.gnu.org/software/bash/manual/bash.html", "platform": "GNU"},
            {"name": "freeCodeCamp — Shell Scripting Tutorial", "url": "https://www.freecodecamp.org/news/shell-scripting-crash-course-how-to-write-bash-scripts-in-linux/", "platform": "freeCodeCamp"},
        ],
        "videos": [{"title": "Bash Scripting Tutorial for Beginners", "youtube_id": "tK9Oc6AEnR4"}],
        "quiz": [
            {"q": "Every bash script should start with…", "options": ["#start", "#!/bin/bash", "//bash", "<script>"], "answer": 1},
            {"q": "How do you reference a variable named NAME?", "options": ["%NAME%", "$NAME", "@NAME", "&NAME"], "answer": 1},
            {"q": "Which operator pipes output of one command into another?", "options": [">", "|", "&&", "::"], "answer": 1},
            {"q": "What does the echo command do?", "options": ["Deletes files", "Prints text to the terminal", "Changes directory", "Lists files"], "answer": 1},
            {"q": "Which symbol redirects output to a file?", "options": ["|", ">", "&", "*"], "answer": 1},
        ],
    },
    "UI/UX Design": {
        "weeks": 3,
        "resources": [
            {"name": "Google — UX Design Foundations (audit free)", "url": "https://www.coursera.org/professional-certificates/google-ux-design", "platform": "Coursera"},
            {"name": "Laws of UX — Free Reference", "url": "https://lawsofux.com/", "platform": "Laws of UX"},
        ],
        "videos": [{"title": "UI/UX Design Tutorial — Wireframe to Design", "youtube_id": "jwCmIBJ8Jtc"}],
        "quiz": [
            {"q": "UX design primarily focuses on…", "options": ["Visual polish only", "How a product feels and works for users", "Server performance", "Marketing copy"], "answer": 1},
            {"q": "A user persona is…", "options": ["A real customer", "A research-based archetype of a target user", "A design pattern", "A color palette"], "answer": 1},
            {"q": "Usability testing is done to…", "options": ["Impress stakeholders", "Observe real users completing tasks", "Test server load", "Validate SEO"], "answer": 1},
            {"q": "A wireframe is a…", "options": ["Final polished design", "Low-fidelity structural layout sketch", "Color palette", "Code prototype"], "answer": 1},
            {"q": "What does a user persona represent?", "options": ["The developer's profile", "A fictional archetype of the target user", "A testing tool", "A brand guideline"], "answer": 1},
        ],
    },
    "Figma": {
        "weeks": 1,
        "resources": [
            {"name": "Figma — Official Beginner Tutorials", "url": "https://help.figma.com/hc/en-us/sections/4405269443991-Figma-for-Beginners-tutorial-4-parts-", "platform": "Figma Help"},
            {"name": "Figma — Community Free Resources", "url": "https://www.figma.com/community", "platform": "Figma"},
        ],
        "videos": [{"title": "Figma Tutorial for Beginners", "youtube_id": "FTFaQWZBqQ8"}],
        "quiz": [
            {"q": "Figma components are used to…", "options": ["Export code", "Reuse consistent design elements", "Run animations only", "Manage fonts"], "answer": 1},
            {"q": "Auto Layout in Figma helps with…", "options": ["Rendering 3D", "Responsive spacing that adapts to content", "Color contrast", "Version control"], "answer": 1},
            {"q": "A Figma prototype is…", "options": ["Production code", "A clickable simulation of the design", "A CSS export", "A wireframe PDF"], "answer": 1},
            {"q": "Figma is primarily a…", "options": ["Code editor", "Collaborative interface design tool", "Database", "Terminal"], "answer": 1},
            {"q": "Components in Figma help with…", "options": ["Writing code", "Reusable, consistent UI elements", "File compression", "Version control"], "answer": 1},
        ],
    },
    "Wireframing": {
        "weeks": 1,
        "resources": [
            {"name": "Figma — What is Wireframing?", "url": "https://www.figma.com/resource-library/what-is-wireframing/", "platform": "Figma"},
            {"name": "NN/g — Wireflows Article", "url": "https://www.nngroup.com/articles/wireflows/", "platform": "Nielsen Norman Group"},
        ],
        "videos": [{"title": "Wireframing Basics for UI/UX", "youtube_id": "qpH7-KFWZRI"}],
        "quiz": [
            {"q": "A wireframe primarily communicates…", "options": ["Final colors", "Layout and structure", "Brand fonts", "Animations"], "answer": 1},
            {"q": "Low-fidelity wireframes are best for…", "options": ["Developer handoff", "Fast early exploration of ideas", "App store screenshots", "Pixel-perfect specs"], "answer": 1},
            {"q": "Wireframes come BEFORE…", "options": ["User research", "High-fidelity mockups", "Problem definition", "Personas"], "answer": 1},
            {"q": "Wireframing comes before…", "options": ["Deployment", "High-fidelity design and prototyping", "User testing", "Server setup"], "answer": 1},
            {"q": "A low-fidelity wireframe focuses on…", "options": ["Exact colors and fonts", "Layout, structure, and content placement", "Animations", "Backend logic"], "answer": 1},
        ],
    },
    "Prototyping": {
        "weeks": 1,
        "resources": [
            {"name": "Figma — Prototyping Guide", "url": "https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma", "platform": "Figma Help"},
            {"name": "IxDF — Prototyping Article", "url": "https://www.interaction-design.org/literature/topics/prototyping", "platform": "Interaction Design Foundation"},
        ],
        "videos": [{"title": "Figma Prototyping Tutorial", "youtube_id": "lTIeZ2ahEkQ"}],
        "quiz": [
            {"q": "The main purpose of a prototype is to…", "options": ["Replace development", "Test ideas with users before building", "Generate code", "Create documentation"], "answer": 1},
            {"q": "High-fidelity prototypes include…", "options": ["Only boxes and lines", "Realistic visuals and interactions", "Server logic", "Database schemas"], "answer": 1},
            {"q": "Prototype feedback should be collected from…", "options": ["Only designers", "Real or representative users", "Competitors", "Nobody"], "answer": 1},
            {"q": "A prototype is used to…", "options": ["Ship the final product", "Simulate user interactions before development", "Store data", "Write documentation"], "answer": 1},
            {"q": "What makes a prototype high-fidelity?", "options": ["It uses pencil on paper", "It closely resembles the final product with real visuals and interactions", "It has no content", "It is static only"], "answer": 1},
        ],
    },
}


def default_module(skill):
    """
    Fallback learning module for skills without a dedicated entry
    (used for bonus skills). All links are real, working search/catalog URLs.
    """
    query = skill.replace(" ", "+")
    return {
        "weeks": 1,
        "resources": [
            {
                "name": f"freeCodeCamp — {skill} articles",
                "url": f"https://www.freecodecamp.org/news/search/?query={query}",
                "platform": "freeCodeCamp",
            },
            {
                "name": f"Coursera — free {skill} courses",
                "url": f"https://www.coursera.org/search?query={query}&price=Free",
                "platform": "Coursera",
            },
        ],
        "videos": [],
        "quiz": [],
    }


def get_module(skill):
    """Return the learning module for a skill, or a real fallback module."""
    return SKILL_MODULES.get(skill, default_module(skill))
