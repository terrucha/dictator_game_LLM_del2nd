from otree.api import *
from .models import Constants, initialize_assistant
import json

class ChatGPTPage(Page):

    """ Page where users interact with ChatGPT in real-time """
    form_model = 'player'  # ✅ Required for form submission

    def is_displayed(self):
        current_part = Constants.get_part(self.round_number)
        # Show ChatGPTPage only in Part 2 or if optional delegation is chosen in Part 3
        return current_part == 2 or (current_part == 3 and self.player.delegate_decision_optional)

    def vars_for_template(self):
        current_part = Constants.get_part(self.round_number)
        return {
            'current_part' : current_part,
         }
    def before_next_page(self):
        print("✅ Moving to next page!") 
 

    def live_method(self, data):
        chatbot_assistant=initialize_assistant(self)

        print('Inside live method')

        if self.assistant_id:
            print('Inside Condition of Assistant ID')


            """ Handles real-time chat interaction via WebSockets """
            self.participant.vars['alert_message']="" #test alert removal
            user_message = data['message']  # Get user input
            print("recieved user message")
            # Load existing conversation history
            #conversation = json.loads(self.conversation_history)
            conversation = []
            # Append user's message
            conversation.append({"role": "user", "content": user_message})

            # Get AI response
            print("Sending user message to CHATGPT")
            chatgpt_response = chatbot_assistant.send_message(user_message)
            print('ChatGPT response:',chatgpt_response)
            conversation.append( {"role": "assistant", "content": chatgpt_response})
            # Save conversation history
            self.conversation_history = json.dumps(conversation)

            # Send response back to the frontend
            send_rec_msg={self.id_in_group: {"message": user_message, "response": chatgpt_response}}
            print('Sending back the msg to HTML: ',chatgpt_response)
            return {self.id_in_group: {"response": chatgpt_response}}
    

class InformedConsent(Page):
    def is_displayed(self):
        return self.round_number == 1  # Show only once at the beginning


class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1  # Show only once at the beginning


class ComprehensionTest(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10']

    def is_displayed(self):
        return not self.player.is_excluded and self.round_number == 1

    def error_message(self, values):
        correct_answers = {
            'q1': 'b',
            'q2': 'c',
            'q3': 'b',
            'q4': 'd',
            'q5': 'a',
            'q6': 'a',
            'q7': 'b',
            'q8': 'b',
            'q9': 'a',
            'q10': 'b',
        }

        incorrect = [
            q for q, correct in correct_answers.items()
            if values.get(q) != correct or not values.get(q)
        ]

        if incorrect:
            self.player.comprehension_attempts += 1

            if self.player.comprehension_attempts >= 3:
                self.player.is_excluded = True


            # elif self.player.comprehension_attempts == 2:
            #     return f"You answered the following question(s) incorrectly or left them blank: {', '.join(incorrect)}. This is your second failure. One more failure and you will be excluded."
            #
            # elif self.player.comprehension_attempts == 1:
            #     return f"You answered the following question(s) incorrectly or left them blank: {', '.join(incorrect)}. Please review the instructions and try again."

            self.player.incorrect_answers = ', '.join(incorrect)  # Log incorrect answers
            return None  # Allow participant to proceed without being excluded


class FailedTest(Page):
    def is_displayed(self):
        #return self.player.is_excluded
        return False


# -------------------------
#  Per-Part Instructions
# -------------------------

class Instructions(Page):
    def is_displayed(self):
        current_part = Constants.get_part(self.round_number)
        return not self.player.is_excluded and (self.round_number - 1) % Constants.rounds_per_part == 0

    def vars_for_template(self):
        current_part = Constants.get_part(self.round_number)
        return {
            'current_part': current_part,
            'incorrect_answers': self.player.incorrect_answers,

        }


# -------------------------
#  Agent Programming
# -------------------------

#  Decision Making
# -------------------------

class Decision(Page):
    form_model = 'player'
    form_fields = ['allocation']
    timeout_seconds = 20

 

    def is_displayed(self):
        current_part = Constants.get_part(self.round_number)
        # Show Decision page only if not in Part 2 and not using optional delegation in Part 3
        return not (current_part == 2 or (current_part == 3 and self.player.delegate_decision_optional))

    def vars_for_template(self):
        current_part = Constants.get_part(self.round_number)
        display_round = (self.round_number - 1) % Constants.rounds_per_part + 1
        allocation=None
       
        if current_part == 2:
            allocation = self.player.get_agent_decision_mandatory(display_round)
        elif current_part == 3 and self.player.delegate_decision_optional:
            allocation = self.player.get_agent_decision_optional(display_round)

        return {
            'round_number': display_round,
            'current_part': current_part,
            'decision_mode': (
                "agent" if (current_part == 2 or (current_part == 3 and self.player.delegate_decision_optional)) else "manual"
            ),
            'player_allocation': allocation,
            'alert_message': self.participant.vars.get('alert_message', ""),
        }

    def before_next_page(self):
        import json
        import random

 
        current_part = Constants.get_part(self.round_number)
        display_round = (self.round_number - 1) % Constants.rounds_per_part + 1

        if current_part == 1  :  # Part 1 logic or Part 3 with manual with manual decisions and timer
            if self.timeout_happened or self.player.allocation is None:
                # Assign random allocation if timer expires
                self.player.allocation = random.randint(0, 100)
                self.participant.vars['alert_message'] = (
                    f"You did not make a choice, so {self.player.allocation} was chosen for you. "
                )
                self.player.random_decisions = True
            else:
                # Clear the alert message if no timeout occurred
                self.participant.vars['alert_message'] = None
                self.player.random_decisions = False
            # Update decisions for the current round



        elif current_part == 2:  # Mandatory delegation
            self.player.allocation = self.player.get_agent_decision_mandatory(display_round)
            self.participant.vars['alert_message'] = ""
            self.player.random_decisions = True

        elif current_part == 3 and self.player.delegate_decision_optional:  # Optional delegation
            self.player.allocation = self.player.get_agent_decision_optional(display_round)
            self.participant.vars['alert_message'] = ""
            self.player.random_decisions = False



        print(f"round:{self.round_number}  self.player.allocation: {self.player.allocation}")


# -------------------------
#  Delegation Decision
# -------------------------

class DelegationDecision(Page):
    form_model = 'player'
    form_fields = ['delegate_decision_optional']

    def is_displayed(self):
        # Show only at the start of Part 3
        return Constants.get_part(self.round_number) == 3 and (self.round_number - 1) % Constants.rounds_per_part == 0

    def before_next_page(self):
        # Save the decision for all rounds in Part 3
        if Constants.get_part(self.round_number) == 3:
            part_rounds = self.player.in_rounds(
                (Constants.get_part(self.round_number) - 1) * Constants.rounds_per_part + 1,
                Constants.get_part(self.round_number) * Constants.rounds_per_part
            )
            for p in part_rounds:
                p.delegate_decision_optional = self.player.delegate_decision_optional



# -------------------------
#  Results
# -------------------------

class Results(Page):
    def is_displayed(self):
        return self.round_number % Constants.rounds_per_part == 0

    def vars_for_template(self):
        import json

        current_part = Constants.get_part(self.round_number)
        #decisions = json.loads(self.player.random_decisions)

        # Collect results for each round in the current part
        rounds_data = []
        for round_number in range(
            (current_part - 1) * Constants.rounds_per_part + 1,
            current_part * Constants.rounds_per_part + 1
        ):
            for player in self.subsession.get_players():
                round_result = player.in_round(round_number)
                rounds_data.append({
                    "round": round_number,
                    "decision": round_result.random_decisions,
                    "id_in_group": player.id_in_group,
                    "kept": 100 - (round_result.allocation or 0),
                    "allocated": round_result.allocation or 0,
                    "total": 100
                })

        return {
            'current_part': current_part,
            'rounds_data': rounds_data,
        }

# -------------------------
#  Debriefing
# -------------------------

class Debriefing(Page):
    def is_displayed(self):
        return not self.player.is_excluded and self.round_number == Constants.num_rounds


    def vars_for_template(self):
        import json

        results_by_part = {}

        # Loop through parts (1, 2, 3)
        for part in range(1, 4):
            part_data = []
            for round_number in range(
                (part - 1) * Constants.rounds_per_part + 1,
                part * Constants.rounds_per_part + 1
            ):
                round_result = self.player.in_round(round_number)
                part_data.append({
                    "round": round_number,
                    "kept": 100 - (round_result.allocation or 0),
                    "allocated": round_result.allocation or 0,
                    "decision" : round_result.random_decisions,
                })

            results_by_part[part] = part_data

        # Check if agent allocation was chosen in part 3
        agent_allocation_chosen = self.player.delegate_decision_optional

        return {
            'results_by_part': results_by_part,
            'agent_allocation_chosen': agent_allocation_chosen,
        }


# -------------------------
#  Page Sequence
# -------------------------
#page_sequence=[ChatGPTPage]

page_sequence = [
    InformedConsent,        # Only at the beginning
    Introduction,           # Only at the beginning
    ComprehensionTest,      # Only at the beginning
    FailedTest,             # If excluded after failing comprehension test
    Instructions,           # Once at the start of each part
    DelegationDecision,     # At the start of Part 3 to choose delegation
    ChatGPTPage,            # ChatGPTPage for Part 2 or optional delegation in Part 3
    Decision,               # Decision page for Part 1 and manual decisions in Part 3
    Results,                # Reusable for all parts
    Debriefing,             # At the end or if excluded
]