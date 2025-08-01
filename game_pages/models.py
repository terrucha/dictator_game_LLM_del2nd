from otree.api import *
from game_pages.chatgptassistant import ChatGPTAssistant


def initialize_assistant(self): 

        chatbot_assistant=ChatGPTAssistant()
        self.assistant_id=chatbot_assistant.assistant_id  

        return chatbot_assistant

class Constants(BaseConstants):
    name_in_url = 'game_pages'
    players_per_group = None  # No groups since it's asynchronous
    num_rounds = 30  # Total rounds (3 parts × 10 rounds)
    endowment = 100  # Amount for Dictator to allocate
    rounds_per_part = 10  # Number of rounds per part

    @staticmethod
    def get_part(round_number):
        """Determine the part of the experiment based on the round number."""
        return (round_number - 1) // Constants.rounds_per_part + 1

class Subsession(BaseSubsession):
    pass
    # aggregated_results = models.LongStringField(blank=True, initial='{}')  # JSON string

    # def creating_session(self):
    #     for player in self.get_players():
    #         if player.random_decisions is None:
    #             player.random_decisions = False
    #            # print(f"[DEBUG] Initialized random_decisions for Player {player.id_in_group}")

    #         if not player.incorrect_answers or player.incorrect_answers.strip() == "":
    #             player.incorrect_answers = ''
    #            # print(f"[DEBUG] Initialized incorrect_answers for Player {player.id_in_group}")

    #         if not player.conversation_history or player.conversation_history.strip() == "":
    #             player.conversation_history = ''




class Group(BaseGroup):
    pass

class Player(BasePlayer):
    app_name = models.StringField(initial='LLM_del2nd')
    final_allocations = models.LongStringField()
    conversation_history=models.LongStringField(initial='[]') #new
    assistant_id = models.StringField(blank=True)  # Allow an empty value
    prolific_id = models.StringField()

    # Allocation for the current decision (manual or agent-based)
    allocation = models.IntegerField(
        min=0,
        max=100,
        label="How much would you like to allocate to the other participant?",
        blank=True
    )

    random_payoff_part=models.IntegerField( blank=True, min=1, max=3 )

    random_decisions = models.BooleanField(blank=True)
    # Tracks the number of failed comprehension attempts
    comprehension_attempts = models.IntegerField(initial=0) #new
    incorrect_answers = models.StringField(initial='') #new

    # Tracks whether the participant is excluded from the study
    is_excluded = models.BooleanField(initial=False)

    gender = models.StringField(
        choices=[
            ('male',        'Male'),
            ('female',      'Female'),
            ('nonbinary',   'Non-binary'),
            ('nosay',       'Prefer not to say'),
        ],
        label="How do you describe yourself?",
        widget=widgets.RadioSelect 
    )

    age = models.IntegerField(
        min=18, max=100,
        label="How old are you?",
    )

    occupation = models.StringField(
        max_length=100,
        label="What is your current main occupation?",
    )

    ai_use = models.StringField(
        choices=[
            ('never',       'Never'),
            ('monthly',     'A few times a month'),
            ('weekly',      'A few times a week'),
            ('daily',       'A few times a day'),
            ('constant',    'All the time'),
        ],
        label="How often do you interact with AI agents (e.g., ChatGPT)?",
        widget=widgets.RadioSelect 
    )

    task_difficulty = models.StringField(
        choices=[
            ('very_diff',   'Very difficult to understand'),
            ('diff',        'Difficult to understand'),
            ('neutral',     'Neutral'),
            ('easy',        'Easy to understand'),
            ('very_easy',   'Very easy to understand'),
        ],
        label="How would you rate the clarity of the experimental task?",
        widget=widgets.RadioSelect 
    )

    feedback = models.LongStringField(
        blank=True,                # optional
        max_length=1000,
        label="Do you have any suggestions or comments about the experiment that you would like to share with the researchers? If yes, use the box below. (Optional)",
    )

    # Fields for comprehension test questions
    q1 = models.StringField(
        label="What is your role in this study?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )
    q2 = models.StringField(
        label="How many parts are there in the task?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )
    q3 = models.StringField(
        label="How many rounds are there in each part of the task?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )
    q4 = models.StringField(
        label="In which part(s) will you make every decision yourself?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )
    q5 = models.StringField(
        label="What happens in Part 2?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )
    q6 = models.StringField(
        label="What is unique about Part 3?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )
    q7 = models.StringField(
        label="True or False: You will always be matched with the same Receiver throughout all 10 rounds in a part.",
        choices=['a', 'b'],
        blank=True
    )
    q8 = models.StringField(
        label="What happens if you do not finalize a decision within 20 seconds?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )
    q9 = models.StringField(
        label="True or False: Only one randomly selected part will be used to determine your bonus payments at the end of the study.",
        choices=['a', 'b'],
        blank=True
    )
    q10 = models.StringField(
        label="What happens if you fail an attention check at the end of a part?",
        choices=['a', 'b', 'c', 'd'],
        blank=True
    )

    # # Agent allocations for Part 2 (mandatory delegation)
    # agent_allocation_mandatory_round_1 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_2 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_3 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_4 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_5 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_6 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_7 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_8 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_9 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_mandatory_round_10 = models.IntegerField(min=0, max=100, blank=True)

    # # Track whether the participant chooses to delegate in Part 3
    delegate_decision_optional = models.BooleanField(
        label="Would you like to delegate your decisions to an AI agent for Part 3?",
        blank=True
    ) 

    # # Agent allocations for Part 3 (optional delegation)
    # agent_allocation_optional_round_1 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_2 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_3 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_4 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_5 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_6 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_7 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_8 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_9 = models.IntegerField(min=0, max=100, blank=True)
    # agent_allocation_optional_round_10 = models.IntegerField(min=0, max=100, blank=True)

    def get_agent_decision_mandatory(self, round_number):
        """Retrieve the agent's allocation for a given round in Part 2."""
        field_name = f"agent_allocation_mandatory_round_{round_number}"
        if hasattr(self, field_name):
            value = getattr(self, field_name)
            if value is None:
                raise ValueError(f"Agent allocation for {field_name} is None.")
            return value
        raise AttributeError(f"Agent allocation for {field_name} not found.")

    def get_agent_decision_optional(self, round_number):
        """Retrieve the agent's allocation for a given round in Part 3."""
        field_name = f"agent_allocation_optional_round_{round_number}"
        if hasattr(self, field_name):
            value = getattr(self, field_name)
            if value is None:
                raise ValueError(f"Agent allocation for {field_name} is None.")
            return value
        raise AttributeError(f"Agent allocation for {field_name} not found.")

    def get_part_data(self):
        """Get all rounds' data for the current part."""
        current_part = Constants.get_part(self.round_number)
        rounds = self.in_rounds(
            (current_part - 1) * Constants.rounds_per_part + 1,
            current_part * Constants.rounds_per_part
        )
        return rounds


