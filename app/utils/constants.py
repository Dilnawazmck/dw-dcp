from enum import Enum

FolderUpperCap: int = 10

NON_OHI_PREFIX: str = "nop"


class NonOhiDataStatus(Enum):
    NEW = "new"
    APPROVED = "approved"


class UserTopicsType(Enum):
    PRACTICE = "practice"
    STANDARD = "standard"
    CUSTOM = "custom"


class CustomTopicsJobAction(Enum):
    CREATE = "create"
    MODIFY = "modify"


class CustomTopicsJobStatus(Enum):
    QUEUE = "queue"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAIL = "fail"


class CustomTopicsJobStatusMessages(Enum):
    CREATE = (
        "Request for custom list has been sent and may take upto {time_taken} to reflect.\nWe will notify "
        "you via email once your list is ready."
    )
    MODIFY = (
        "Request for modifying custom list has been sent and may take upto {time_taken} to reflect.\nWe will"
        " notify you via email once your list is ready."
    )


DEFAULTFOLDER: str = "Default"

USER: str = "user"
ADMIN: str = "admin"
SUPER_ADMIN: str = "superadmin"

OHI_OUTCOMES_AND_PRACTICES = [
    {
        "category": "Leadership",
        "sub_category": [
            "Authoritative leadership",
            "Consultative leadership",
            "Supportive leadership",
            "Challenging leadership",
        ],
    },
    {
        "category": "Work Environment",
        "sub_category": [
            "Open and trusting",
            "Performance transparency",
            "Operationally disciplined",
            "Creative & entrepreneurial",
        ],
    },
    {
        "category": "Accountability",
        "sub_category": [
            "Role clarity",
            "Performance contracts",
            "Consequence management",
            "Personal ownership",
        ],
    },
    {
        "category": "Coordination and Control",
        "sub_category": [
            "People performance review",
            "Operational management",
            "Financial management",
            "Professional standards",
            "Risk management",
        ],
    },
    {
        "category": "Capabilities",
        "sub_category": [
            "Talent acquisition",
            "Talent development",
            "Process based capabilities",
            "Outsourced expertise",
        ],
    },
    {
        "category": "Motivation",
        "sub_category": [
            "Meaningful values",
            "Inspirational leaders",
            "Career opportunities",
            "Financial  incentives",
            "Rewards and recognition",
        ],
    },
    {
        "category": "External orientation",
        "sub_category": [
            "Customer focus",
            "Competitive insights",
            "Business partnerships",
            "Government and community relations",
        ],
    },
    {
        "category": "Innovation and learning",
        "sub_category": [
            "Top-down innovation",
            "Bottom-up innovation",
            "Knowledge sharing",
            "Capturing external ideas",
        ],
    },
]


STANDARD_THEMES = [
    ["Communication", "decision", "dadas", "dadas", "dadsada"],
    ["Cross-Team Collaboration", "Cross-Team Collaboration"],
    ["Innovation", "Innovation"],
    ["Compensation and Benefits", "Compensation and Benefits"],
    ["Transparency", "Transparency"],
    ["Training and Learning Opportunities", "Training and Learning Opportunities"],
    ["Hiring and Recruiting", "Hiring and Recruiting"],
    ["Teamwork", "Teamwork"],
    ["Management", "Management"],
    ["Senior Leadership", "Senior Leadership"],
    ["Tools and Infrastructure", "Tools and Infrastructure"],
    ["Values and Culture", "Values and Culture"],
    ["Accountability and Responsibility", "Accountability and Responsibility"],
    ["Decision-Making", "Decision-Making"],
    ["Customer Focus", "Customer Focus"],
    [
        "Work-Life Balance",
        "Sufficient personal time",
        "Managable work",
        "work culture",
        "culture",
    ],
    ["Diversity", "Diversity"],
    ["Quality of Products and Services", "Quality of Products and Services"],
    ["Company Vision", "Company Vision"],
    [
        "Process and Organizational Effectiveness",
        "Process and Organizational Effectiveness",
    ],
    ["Company Brand", "Company Brand"],
    ["Survey Feedback", "Survey Feedback"],
    ["Recognition and Appreciation", "Recognition and Appreciation"],
    ["Meaningful Work", "Useful Work", "Good coding practice"],
    ["Sales", "Sales"],
    ["Career Growth Opportunities", "Career Growth Opportunities"],
    ["Documentation", "Documentation"],
    ["Perks", "Perks"],
    ["Meetings", "Meetings"],
    ["Commute", "Commute"],
    ["Autonomy", "Autonomy"],
    ["Physical Workspace", "Physical Workspace"],
    ["Remote Sites", "Remote Sites"],
]


UNCLASSIFIED_CATEGORY: str = (
    "Unclassified"  # This should match with the DB metadata for topics and practice
)
MIN_SENTENCE_LENGTH: int = 5
MIN_THRESHOLD: float = 0.10

MODEL_SENTIMENT_TAGGING_DICT = {0: "Negative", 1: "Neutral", 2: "Positive"}

NON_OHI_REQUEST_PER_USER = 5

COMMENT_LENGTH_FOR_TAGGING = 3000
