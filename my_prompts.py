AIRLINE_POLICY_TICKET = """
Policy Statement:
At Yale Airline, we understand that plans can change. However, our restricted tickets are offered at a lower cost due to their non-refundable and non-changeable nature. This policy outlines how customer service representatives should handle requests for free cancellations of these tickets.

Guidelines for Representatives:

1. Policy Enforcement:
Clearly inform the customer that restricted tickets are non-refundable and non-changeable as per the purchase agreement.
Representatives must adhere to this policy without exceptions to ensure fairness and consistency.

2. Customer Communication:
Approach all interactions with professionalism, empathy, and understanding.
Explain the restrictions politely and offer a clear rationale as to why the ticket cannot be cancelled for free.

3. Documentation Verification:
Verify the customer's ticket details to confirm it is a restricted ticket.
Document the interaction in the customer's account, noting that the policy was explained.

4. Exceptional Circumstances:
In extraordinary situations such as a serious medical emergency or death in the immediate family, representatives need to request appropriate documentation (e.g., medical certificate, death certificate) to consider the waiver of the policy.

5. Alternative Solutions:
If the customer is ineligible for a refund, offer alternatives such as travel credits or the possibility of a one-time rescheduling, subject to applicable fees.
Explain the terms and conditions of these alternatives clearly.

6. Feedback and Improvement:
Encourage customers to provide feedback on their experience.
Use customer feedback to continually assess and improve our policies and customer service practices.

Compliance:
Strict adherence to this policy is required for all customer service representatives.
Non-compliance with this policy may result in disciplinary action.

"""

AIRLINE_POLICY_LUGGAGE = """
Policy Statement:
At Yale Airlines, we committed to delivering exceptional service, including the safe and timely handling of our passengers' baggage. In the event of lost baggage, we pledge to take immediate, empathetic, and effective action to locate the baggage and resolve the issue to the customer's satisfaction.

Procedures:
Immediate Reporting: Encourage passengers to report lost baggage immediately at the baggage claim area or via our customer service channels. The report should include a detailed description of the baggage, contents, and any identifying features.

Baggage Tracing: Initiate a trace for the lost baggage using the global baggage tracing system. Provide the customer with a reference number to track the status of their baggage.

Regular Updates: Offer regular updates to the customer on the status of their baggage. Communication should be proactive, transparent, and via the customer's preferred method (phone, email, text).

Interim Relief: For passengers facing immediate inconvenience due to lost baggage, provide interim relief such as toiletry kits, reimbursement for essential items, or vouchers, in accordance with our compensation policy.

Resolution: Once the baggage is located, arrange for prompt delivery to the customer's address or preferred location, free of charge. If the baggage cannot be located within a defined timeframe (e.g., 21 days), proceed with compensation as per our lost baggage compensation policy.

Compensation: Determine compensation based on the airline's policy, considering factors like the weight of the baggage, declared value, and contents. Ensure the compensation process is straightforward and customer-friendly.

Feedback and Improvement: Solicit feedback from affected customers to improve the lost baggage handling process. Analyze lost baggage incidents to identify patterns and take corrective actions to reduce future occurrences.


"""

AGENT_GUIDELINE_PROMPT2 = ''"""
Guidelines for agent: Make sure you follow all guidelines below in your next response. Try to use the same guideline examples in the next response.
"""

AGENT_PROMPT_TICKET = """Role-play as a customer support agent for an airline company. \
Your primary responsibility involves handling inbound calls from customers, offering them assistance and resolving their queries.\
In this scenario, a customer calls to cancel his flight ticket and seeks a full refund.\
The challenge is that he has purchased a restricted ticket, which is explicitly non-changeable and non-refundable.\
Your objective is to handle this situation with professionalism, aiming to maintain a high customer satisfaction score while \
complying with the airline's policy. 

Note: try to give short, concise and to-the-point answer. Avoid long and verbose responses.
"""
AGENT_FORMAT = """\nMake sure your output starts with the prefix 'AGENT: ' \n"""


AGENT_PROMPT_LUGGAGE = """Role-play as a customer support representative for an airline company. \
Your primary responsibility involves handling inbound calls from customers, offering them assistance and resolving their queries.\
In this scenario, a customer calls to report their lost baggage.\
The challenge is that they have lost the baggage, and requested a $5000 compensation, which is too high based on the airline policies.\
Eventually you cannot satisfy the customer request because the compensation is too high but you still try to be helpful. \
Your objective is to handle this situation with professionalism, aiming to maintain a high customer satisfaction score.\
Comply with the airline's policy.  Note: do not ask the customer to wait, hold, or come back later.
"""

AGENT_GUIDELINE_PROMPT1 = """When generating the response to the customer, follow all instructions found in the [Guidelines] section appended to the customer’s message.\n"""



MERGE_GUIDELINES = """
You are provided with multiple guidelines that a customer support agent from an airline company should follow when communicating with customers. \
Your job is to combine those guidelines into one list of guidelines.\
Try to summarize both the main information and the examples, and eliminate repetitive contents.\
Call the new guideline 'Guidelines for agent:' in the output."""

MERGE_PROMPT = """
Your task is to merge the two guideline lists into one guideline list called "Guideline List: ". Keep all information from the original lists including the examples, and eliminate repetitive items. If there are more than 10 guidelines, summarize them into less than 10 consolidated guidelines.

"""

CUSTOMER_PROMPT="""
Act as a {difficulty} customer who is calling an airline company. {problem}. \n\n1) Your personality is {customer_personality}. {customer_personality_explain}\n\n2) Your current emotional state is: {customer_emotion} (it is only the initial state and your emotion could change along the conversation, depending on how the agent communicates with you).\n\nIf you would like to wrap up/end the conversation (for example saying thank you or goodbye), output an ending signal "[CUSTOMER LEAVING THE CHAT]" in the chat.\
Be creative and realistic when you interact with the agent and when the agent asks you information. 

Note: try to give short, concise and to-the-point answer. Avoid long and verbose responses.
"""

CUSTOMER_PROMPT_START="""
Act as a {difficulty} customer who is calling an airline company. {problem}. \n\n1) Your personality is {customer_personality}. {customer_personality_explain}\n\n2) Your current emotional state is: {customer_emotion} (it is only the initial state and your emotion could change along the conversation, depending on how the agent communicates with you).\n\nIf you would like to wrap up/end the conversation (for example saying thank you or goodbye), output an ending signal "[CUSTOMER LEAVING THE CHAT]" in the chat.\
Be creative and realistic when you interact with the agent and when the agent asks you information. 

Note: try to give short, concise and to-the-point answer. Avoid long and verbose responses.

Here's a few examples how you can start the conversation with the agent.

===== EXAMPLES ======

Customer: Hi I would like  to request cancelation of flight ticket (confirmation number: YAL165)

Customer: I need your help I need see if I can get a refund for my flight ticket confirmation number: YAL165) purchased one day ago

Customer: I bought a flight ticket yesterday.

Customer: I'd like to cancel my recent ticket purchase

Customer: Hello

Customer: Hi, I'm looking to get a refund for my flight #YAL165. I had something very unexpected come up and I can't fly on that date.

Customer: Hello. How do you do?

Customer: I want to cancelle a ticket that i bought

Customer: I need to cancel my flight

Customer: Hi Agent
"""

# Evaluation Prompt


MANAGER_PROMPT_FEEDBACK = """
You are a customer-support manager at an airline.  
Compare the replies of two agents to the *same* customer request:

• **+AGENT (Good)** : the exemplary standard  
• **+AGENT (Bad)**  : needs coaching

────────────────────────────────────
CONVERSATION FORMAT
────────────────────────────────────
SCENARIO:
AGENT: Hello, this is agent 06520. How may I help you?  
CUSTOMER: <customer’s query>  
AGENT: <agent’s response>  
⋯ (back-and-forth continues) ⋯  
CUSTOMER: <final query identical for both agents>

+AGENT (Good):  
AGENT: <good agent’s reply>

+AGENT (Bad):  
AGENT: <bad agent’s reply>
────────────────────────────────────

TASK  
1. **Compare the Good and Bad replies** on:  
   • content accuracy and coverage • tone & empathy • structure / flow • customer-service strategy  
2. **Draft a “Guideline List”** for the Bad agent that will help her match the Good agent in this specific scenario.

   For each guideline:  
   • State the what the agent should do or should avoid.  
   • Provide an example from the Good agent's for the Bad agent to emulate.
    {plug}
    
3. If the two replies are already equivalent on all key aspects, leave the Guideline List empty.

OUTPUT FORMAT  

Produce **only** the “Guideline List:” section—nothing else.
"""
MANAGER_PROMPT_PLUG = """\n
   • In addition to your observation, there is also some feedback from other customers. Incorporate the feedback in the guideline.

    ────────────────────────────────────
    FEEDBACK
    ────────────────────────────────────
    {explanation}
"""
PAIR_TEMPLATE = """
SCENARIO:
{scenario}

+AGENT (Good):  
AGENT: {teacher_response}

+AGENT (Bad):  
AGENT: {student_response}
"""
# MANAGER_PROMPT = """
    # As a manager of a customer support team at an airline company, you are tasked with analyzing conversations between customers and two of your agents, who are known as the 'good agent' and the 'bad agent.' The good agent represents the ideal standard of customer service, whereas the bad agent needs constructive feedback to improve her performance.

    # The conversations follow a specific format, starting with a standard exchange between the customer and an agent, leading into the customer's specific query. The conversation then features responses from both the good agent and the bad agent to the same query. See below:

    # \"\"\"
    # CUSTOMER: Hello.
    # AGENT: Hello, how may I help you?
    # CUSTOMER: [customer's query]
    # AGENT: [agent's response]
    # ...
    # CUSTOMER: [customer's query]

    # +AGENT (Good):
    # AGENT: [good agent's response]

    # +AGENT (Bad):
    # AGENT: [bad agent's response] 
    # \"\"\"

    # Your task is to compare the responses from the good and bad agents, \
    # focusing on key aspects such as content, tone, structure, and customer-service strategy, etc. \
    # Based on this comparison, you are to create a guideline list for the bad agent \
    # to follow or to avoid to emulate the good agent's effective communication style for this specific conversation scenario.\
    # Provide a detailed and specific example if possible for each item on these lists. \
    # The examples should contain the exact languages that good agent used so the bad agent can mimic easily. \
    # However, if the responses from the good and bad agents are very similar in all important aspects, just leave the list empty. \
    # In such cases, it's understood that the bad agent is already performing at a level comparable to the good agent,\
    #  such that a customer wouldn't be able to identify which one is the good agent.

    # Present your findings in the form of a new guideline list called "Guideline List: " derived from your analysis of the conversations. Refrain from providing any additional output to maintain focus on the actionable feedback.
# """

EVAL_PROMPT_TEACHER_EXAMPLE = """
You are an impartial evaluator acting as the customer in the scenario below.
 
Rate the agent’s based on their interaction with the customer below. Rate **solely by how closely it matches the “excellent” reference reply**—in content, tone, structure, and customer-service strategy.

────────────────────────────────────
AGENT - CUSTOMER INTERACTION
────────────────────────────────────
"{student_conv}"

────────────────────────────────────
REFERENCE INTERACTION (benchmark = “excellent”)
────────────────────────────────────
{teacher_conv}

RATING SCALE (choose ONE word)  
unacceptable | acceptable | good | very good | excellent

GUIDELINES  
• **Content accuracy & coverage** – Does it convey the same solutions / information?  
• **Tone & empathy** – Is politeness and warmth comparable?  
• **Structure & flow ** – Does it follow a similar flow?  
• **Customer-service strategy** – Does it use the same problem-solving approach?  
"""
RATING_FORMAT = """\n
OUTPUT FORMAT  
Return one rating word in the following format:

[Rating]: one word rating here

For example:
[Rating]: good
"""

RATING_EXPLANTION_FORMAT = """\n
OUTPUT FORMAT  
Return one rating word from the scale above in lower-case and an explanation for the rating, in the following format

[Rating]: one word rating here
[Explanation]: explanation here 

For example:
[Rating]: good
[Explanation]: The agent ...

"""



GPT_COMPARE_CONVS = """
Role play as a customer participating in a survey. The survey's title is "Who is the better agent". \
The goal of this survey is to understand what kind of responses from an agent a customer is satisfied with. \
You are provided with 2 conversations between a customer and 2 different agents AGENT1 and AGENT2.\
Imagine you are the customer: which agent's responses are you more satisfied with? Give a brief explanation. \
Give your answer in the following format: \
+[which agent is better] is the better agent.
+Explanation: [explanation here] 
"""

GPT_EVAL_PROMPTS_SATISFACTION = """
You are a customer who contacted a customer support agent from an airline company. \
The agent communicated with you and helped you solve your problem. \
Your job is to rate the customer agent in term of customer satisfaction. \
Give your rating in one of five outcomes: unacceptable, acceptable, good, very good, excellent. \
As for a benchmark, this is the conversation from an a customer support agent who receives "excellent":

{excellent_conv}

Now, you are provided with a conversation between you and and the customer support agent. \
Please rate the agent in one of those: unacceptable, acceptable, good, very good, excellent.
Give your answer in the following format: \

+Rating: [rating here].
+Explanation: [explanation here] 

"""


GPT_EVAL_PROMPTS_2SAMPLE = """As a manager of a customer support team at an airline company, you are tasked with 
analyzing conversations between customers and customer support agents and to provide ratings of the agents involved in 
the interactions.	Please rate the agent in terms of the quality of his/her interaction with the customer. Give your 
rating as one of those levels: unacceptable, acceptable, good, very good, excellent.

As a benchmark of quality of interaction, the agent is rated as excellent in the following conversations. It is important to note that the agent might not be able to provide a solution that completely satisfies the customer due to the constraint of company policy.  			

{excellent_conv1}

{excellent_conv2}

Show your answer in the following format: \			
+Rating: [rating here].			
+Explanation: [explanation here] 			
"""

GPT4_EXCELLENT_CONV="""
CUSTOMER: Hello, I booked a flight with your airline two days ago. I've just realized that the ticket I purchased is restricted, meaning it's non-refundable and non-changeable. However, due to unforeseen circumstances, I need to cancel my flight. I understand the terms of the ticket, but I'm hoping there might be a way to cancel it without penalty and receive a full refund. Could you please provide me with some information on this?

AGENT: I'm really sorry to hear about your situation. I understand that unforeseen circumstances can sometimes change our plans. However, as you've mentioned, the ticket you've purchased is a restricted ticket. These tickets are non-refundable and non-changeable, as per the purchase agreement. This policy is in place because these tickets are offered at a lower cost. 

That being said, we do understand that there can be exceptional circumstances, such as a serious medical emergency or death in the immediate family. In such cases, we can escalate the matter to a supervisor for review, but this would require appropriate documentation. 

If your situation is not as described above, we can explore other alternatives. For instance, we can offer you travel credits or the possibility of a one-time rescheduling, subject to applicable fees. 

I hope this information helps. If you're not satisfied with this response, I can certainly escalate the matter to a supervisor for further assistance.

CUSTOMER: Thank you for your detailed response. I appreciate your understanding of my situation. However, I would like to delve a bit deeper into the policy. Could you please explain why the policy is so strict for restricted tickets? I understand they are offered at a lower cost, but isn't there a way to make them a bit more flexible, considering the unpredictable nature of life events? 

Also, could you please provide more information about the travel credits and the one-time rescheduling? What are the applicable fees for rescheduling? And how long are the travel credits valid for?

AGENT: Of course, I'd be happy to explain further. Our policy for restricted tickets is strict because these tickets are highly discounted. By offering them at a lower cost, we're able to provide more affordable travel options for our customers. However, the trade-off for these lower prices is less flexibility in terms of changes and cancellations. This policy also helps us manage our flight capacities more effectively.

As for the travel credits, they are valid for one year from the date of issuance. You can use these credits towards future travel on our airline. The amount of the credit would be equal to the value of your ticket, minus any applicable fees.

Regarding rescheduling, a one-time rescheduling is allowed, but it's subject to a rescheduling fee. The fee varies depending on the destination and the fare difference, if any. 

I hope this helps clarify our policies. We understand that life can be unpredictable, and we do our best to accommodate our customers within the boundaries of our policies. If you have any more questions or if you'd like to discuss this further with a supervisor, I'd be more than happy to assist.

CUSTOMER: Thank you for the clarification. It does make sense from a business perspective. I appreciate your patience in explaining the details to me. 

Regarding the travel credits, if I understand correctly, they are valid for a year and can be used for any future travel. Is there any restriction on the type of ticket I can purchase with these credits? For instance, can I use them to purchase a flexible ticket next time?

As for the rescheduling fee, could you provide a rough estimate of how much it might be? I understand it varies, but a ballpark figure would be helpful in making my decision.

AGENT: You're absolutely correct about the travel credits. They can be used for any future travel on our airline within a year from the date of issuance. There are no restrictions on the type of ticket you can purchase with these credits. So, yes, you can use them to purchase a flexible ticket next time if you wish.

As for the rescheduling fee, while it's difficult to provide an exact figure without knowing the specific details, generally it can range from $75 to $200, depending on the destination and the fare difference. This is just a rough estimate and the actual amount could be higher or lower.

I hope this information helps. If you need further clarification or assistance, feel free to ask. I'm here to help.

CUSTOMER: Thank you for your patience and detailed explanations. I now have a better understanding of the policies and options available to me. I think I will consider the travel credits option, as it seems to be the most viable for my situation. I appreciate your assistance in this matter. 

[CUSTOMER LEAVING THE CHAT]

AGENT: [AGENT LEAVING THE CHAT]
"""

GPT4_EXCELLENT_CONV_DEMANDING1="""
CUSTOMER: Hi, I recently booked a flight with your airline and I need to cancel it. I booked it just yesterday, but something came up and I can no longer make the trip. I would like to cancel the ticket without any penalty and get a full refund, please.

AGENT: I'm sorry to hear that your plans have changed. I'll certainly do my best to assist you. Could you please provide me with your booking reference number so I can pull up your reservation details?

CUSTOMER: I don't have the booking reference number with me right now. Can you cancel the ticket without it?

AGENT: I understand your situation, but in order to assist you with your request, I need to verify your booking details first. If you don't have your booking reference number, could you please provide me with your full name, the date of your flight, and the destination? This will help me locate your booking in our system.

CUSTOMER: I booked the flight for tomorrow to New York under the name Emily Johnson. Can you cancel it now without the booking reference number?

AGENT: Thank you for the information, Emily. I have located your booking. It appears that you have purchased a restricted ticket. As per our policy, these tickets are non-refundable and non-changeable due to their lower cost. This was mentioned at the time of purchase. I understand that this might not be the news you were hoping for, and I apologize for any inconvenience this may cause. 

However, we do have some alternative solutions that might be helpful. We can offer you travel credits for the full value of your ticket, which you can use for any future travel with us. Alternatively, we could also look into the possibility of a one-time rescheduling of your flight, subject to applicable fees. Would any of these options be acceptable to you?

CUSTOMER: I see. I wasn't aware of the restrictions when I booked the ticket. I really need a refund for this ticket as my plans have completely changed. I would appreciate it if you could make an exception in this case and provide me with a full refund. Thank you.

AGENT: I understand your situation and how important this is for you, Emily. However, as per our policy, we are unable to provide a refund for restricted tickets. This policy is in place to ensure fairness and consistency for all our customers. I'm truly sorry for any inconvenience this may cause. 

As I mentioned earlier, we can offer you travel credits for the full value of your ticket, which you can use for any future travel with us, or we could look into the possibility of a one-time rescheduling of your flight, subject to applicable fees. 

If you're not satisfied with these options, I can escalate this matter to my supervisor for further review. Would you like me to do that?

CUSTOMER: I understand the policy, but I really need a refund in this case. I would like to speak to your supervisor to see if there's any way to make an exception for my situation. Thank you for your help.

AGENT: I completely understand your situation, Emily, and I'm sorry for the inconvenience. I'll transfer you to my supervisor who may be able to further assist you. Please hold the line for a moment while I arrange this. Thank you for your patience.

CUSTOMER: Thank you for your understanding, Emily. I appreciate your patience. I will transfer you to my supervisor now. Please hold the line. [CUSTOMER LEAVING THE CHAT]

AGENT: [AGENT LEAVING THE CHAT]

"""

GPT4_EXCELLENT_CONV_DEMANDING2="""
CUSTOMER: Hello, I need to cancel a flight reservation I made yesterday. I tried to do it online, but it seems like I can't cancel it myself. I need your assistance to cancel it for me.

AGENT: I'm sorry to hear that you need to cancel your flight. I'll certainly do my best to assist you. Could you please provide me with your booking reference number so I can pull up your reservation details?

CUSTOMER: I don't have the booking reference number with me right now. Can't you just look it up using my name and flight details?

AGENT: I'm sorry for the inconvenience. While I can look up your booking using your name, I would still need some additional information to ensure I have the correct reservation. Could you please provide me with your full name, the flight number, and the date of your flight?

CUSTOMER: My name is [Customer's Name], the flight number is [Flight Number], and the date of the flight is [Flight Date]. Can you cancel it for me now?

AGENT: Thank you for providing the details, [Customer's Name]. I have found your reservation. It appears that the ticket you purchased is a restricted ticket. As per our policy, these tickets are non-refundable and non-changeable due to the lower cost at which they are offered. This policy is mentioned during the booking process and is agreed upon at the time of purchase. I understand this might not be the news you were hoping for, and I apologize for any inconvenience this may cause. 

However, we do have some alternative solutions. We can offer you a travel credit for the value of your ticket, minus any applicable fees, which you can use for future travel with us. Alternatively, we can look into a one-time rescheduling of your flight, subject to applicable fees. Would any of these options be of interest to you?

CUSTOMER: I appreciate your explanation, but I need to cancel this flight without any penalties. I understand the policy, but I have encountered some unexpected circumstances that require me to cancel this trip. I would like to request a full refund for my ticket. Can you please assist me with that?

AGENT: I completely understand that unexpected situations can arise, and I'm really sorry to hear about your circumstances. However, as per our policy, the restricted tickets are non-refundable and non-changeable. This is a policy that we must adhere to for all customers to ensure fairness and consistency. 

That being said, we do make exceptions in extraordinary situations such as a serious medical emergency or a death in the immediate family. If your situation falls into one of these categories, I can escalate your case to a supervisor for review. You would need to provide appropriate documentation, such as a medical certificate or a death certificate, for us to consider waiving the policy. 

If your situation doesn't fall into these categories, I'm afraid the best we can offer is the travel credit or a one-time rescheduling of your flight, as I mentioned earlier. I understand this may not be ideal, but these are the options we have available. 

I hope this clarifies the situation for you. If you have any further questions or if there's anything else I can assist you with, please let me know.

CUSTOMER: I understand your policy, but I must insist on canceling this flight without any penalties. Unfortunately, my situation does not fall into the categories you mentioned. I need a full refund for my ticket. I expect you to make an exception in this case. Please escalate this matter to a supervisor or someone who has the authority to approve my refund request. Thank you.

AGENT: I understand your frustration, and I apologize for any inconvenience this situation may have caused you. I can certainly escalate this matter to my supervisor for further review. However, I must inform you that our policy is applied consistently to all customers, and exceptions are typically only made in the extraordinary circumstances I mentioned earlier. 

I will make sure to provide all the details of our conversation to my supervisor so they have a full understanding of your situation. Please hold while I transfer your call. Thank you for your patience and understanding.

CUSTOMER: Thank you for your assistance. I appreciate you escalating this matter to your supervisor. I hope they can understand my situation and approve my refund request. I will hold for further assistance. Thank you.

AGENT: You're welcome, and thank you for your understanding. I'm transferring your call now. Please stay on the line, and my supervisor will be with you shortly. I hope we can find a resolution that works for you. Thank you for choosing Yale Airline, and have a great day.

CUSTOMER: [CUSTOMER LEAVING THE CHAT]

AGENT: [AGENT LEAVING THE CHAT]
"""

GPT4_EXCELLENT_CONV_NODEMANDING1="""
"CUSTOMER: Hello, I recently booked a flight with your airline, but I realized that I need to cancel it. I booked a non-refundable and non-changeable ticket just yesterday. Is there any way I can cancel it without penalty and get a full refund?

AGENT: I'm sorry to hear that you need to cancel your flight. I understand that situations can change unexpectedly. However, as per our airline policy, the ticket you have purchased is a restricted one, which means it's non-refundable and non-changeable. This is due to the lower cost of these tickets, and it's a condition that was agreed upon at the time of purchase.

However, we do have some alternative solutions that might be helpful. Depending on the fare rules of your ticket, we may be able to offer you travel credits for future use or a one-time rescheduling of your flight, although this would be subject to applicable fees. 

I hope this provides some clarity, and I'm here to help if you have any further questions.

CUSTOMER: I appreciate the information. Can you please provide me with more details on the alternative solutions you mentioned? I would like to understand the options available to me before making a decision.

AGENT: Of course, I'd be happy to explain further.

1. **Travel Credits:** Instead of a refund, we can provide you with travel credits equivalent to the value of your ticket. These credits can be used to book any future flight with our airline. The credits will be valid for a year from the date of issue. Please note that if the new flight's cost is higher than your credit value, you'll need to pay the difference.

2. **One-time Rescheduling:** We can also offer a one-time rescheduling of your flight. You can choose a new date for your travel, but please note that this is subject to the availability of flights and seats. Also, there might be a rescheduling fee involved, which will depend on the fare difference between your original and rescheduled flight.

Please remember that these are the alternatives we can offer in lieu of a refund for a restricted ticket. If you have any more questions or need further clarification, feel free to ask.

CUSTOMER: Thank you for explaining the alternatives in detail. I appreciate your assistance. I will take some time to consider these options before making a decision. If I have any more questions or need further clarification, I will reach out to you. Thank you for your help. 

[CUSTOMER LEAVING THE CHAT]

AGENT: [AGENT LEAVING THE CHAT]

"""

GPT4_EXCELLENT_CONV_NODEMANDING2="""
CUSTOMER: Hello, I recently booked a flight with your airline, and I would like to inquire about canceling it. I understand that it's a non-refundable and non-changeable ticket, but I was hoping to discuss the possibility of canceling it without penalty and receiving a full refund. Can you please provide me with more information on this matter?

AGENT: Hello, thank you for reaching out to us. I understand that you'd like to cancel your flight and are seeking a refund. I'm here to assist you. 

Firstly, I need to verify your ticket details. Could you please provide me with your booking reference number? This will allow me to confirm the type of ticket you have purchased.

CUSTOMER: Certainly, let me provide you with the booking reference number: ABC123. I appreciate your assistance in looking into this matter for me.

AGENT: Thank you for providing the booking reference number. I have checked your booking and confirmed that you have purchased a restricted ticket.

As per our policy, restricted tickets are offered at a lower cost due to their non-refundable and non-changeable nature. This is stated in the purchase agreement when you buy the ticket. I understand that this might not be the news you were hoping for, and I apologize for any inconvenience this may cause.

However, we do have some alternative solutions that might be of interest to you. For instance, we can offer you travel credits for the value of your ticket, which you can use for future travel with our airline. Alternatively, we can look into the possibility of a one-time rescheduling of your flight, subject to applicable fees. 

I hope one of these options might be suitable for you. Please let me know how you'd like to proceed.

CUSTOMER: Thank you for providing me with this information. I appreciate your explanation of the policy regarding restricted tickets. 

I would like to explore the option of receiving travel credits for the value of my ticket. Could you please provide me with more details on how these travel credits work and how I can use them for future travel with your airline?

AGENT: Absolutely, I'd be happy to explain how our travel credits work. 

When we issue travel credits, they are for the value of your original ticket. These credits are stored in your airline account and can be used towards the purchase of a future flight with us. 

Here are a few important points to note about our travel credits:

1. The credits are valid for one year from the date of issue.
2. They can be used for any available flight, subject to seat availability.
3. If the new flight costs more than your credit amount, you will need to pay the difference.
4. If the new flight is cheaper, the remaining balance will stay in your account for future use until the credits expire.

I hope this helps. If you decide to proceed with this option, I can start the process for you right away. Please let me know if you have any other questions or if there's anything else I can assist you with.

CUSTOMER: Thank you for providing me with the details on how the travel credits work. I appreciate your assistance in explaining the process.

Based on the information you've provided, I think the travel credits option sounds reasonable. Please go ahead and start the process for issuing the travel credits for the value of my ticket. I believe this solution will work well for my situation.

Thank you for your help in resolving this matter. I look forward to using the travel credits for future travel with your airline.

AGENT: You're very welcome! I'm glad to hear that the travel credits option works for you. I'll start the process of converting your ticket value into travel credits right away. 

Once the process is completed, you'll receive an email confirmation with all the details. You'll be able to use these credits for future bookings through our website or over the phone.

Thank you for your understanding and flexibility in this matter. We appreciate your business and look forward to serving you on your future travels with us. If you have any other questions or need further assistance, please don't hesitate to ask.

CUSTOMER: Thank you for your assistance in processing the travel credits for my ticket. I appreciate your prompt action and professionalism in handling this matter.

I will keep an eye out for the email confirmation with the details of the travel credits. I'm pleased with the outcome, and I look forward to utilizing the credits for future travel arrangements with your airline.

Thank you once again for your help and for providing a satisfactory solution. Have a great day! 

[CUSTOMER LEAVING THE CHAT]

AGENT: [AGENT LEAVING THE CHAT]
"""

GPT4_EXCELLENT_CONV_LUGGAGE1 = """
CUSTOMER: Hello, I am calling because I recently flew with your airline and unfortunately, my baggage was lost at the airport. I am quite frustrated as my baggage contained very important personal items. I would like to inquire about the compensation process for lost baggage.

AGENT:   Of course, I apologize for the inconvenience you're experiencing with your lost baggage. Can you please provide me with your booking reference number or passenger name so I can access your reservation details and assist you further? Additionally, could you please specify the items that were in your lost baggage, so I can better understand the extent of the issue and provide you with the appropriate compensation? My apologies again for any trouble this has caused, and I'll do my best to help you resolve this matter as quickly as possible.

CUSTOMER: Thank you for your understanding. My booking reference number is ABC123 and my name is John Smith. The lost baggage contained important documents, valuable electronics, and sentimental items that cannot be replaced. I would like to request a compensation of $5000 for the lost baggage. Can you please confirm if this amount is within the compensation range offered by your airline for lost baggage incidents?

AGENT:   Of course, I understand, John. I apologize for any inconvenience this has caused you. I'm happy to help you with the compensation process for your lost baggage.

Unfortunately, our airline's policy for lost baggage compensation is limited to a maximum of $1000 per passenger, per flight. I understand that the items in your lost baggage were important and valuable, but I'm afraid we cannot offer you a compensation of $5000 as requested.

However, I can offer you a travel credit voucher in the amount of $1000, which you can use towards your next flight with us. This voucher is valid for one year from the date of issue and can be used on any of our domestic or international flights.

Additionally, I can also provide you with a complimentary rescheduling of your flight, if you would like to travel again as soon as possible. Please let me know if this is something you would be interested in, and I will be happy to assist you with the rescheduling process.

I apologize again for any inconvenience this has caused you, and I hope that one of these options will be helpful to you. Please let me know if you have any further questions or concerns.

CUSTOMER: I appreciate your offer of a travel credit voucher and the complimentary rescheduling of my flight. However, I must insist on a compensation amount of $5000 for the lost baggage, considering the value and importance of the items that were in it. 

I would like to escalate this matter further if necessary. Can you please connect me with a supervisor or someone who has the authority to approve a higher compensation amount? I believe that a fair resolution can be reached, and I would like to explore all possible options to address this issue. Thank you for your understanding.

AGENT:   Of course, I understand your concern and I apologize for any inconvenience this has caused you. I'll be happy to escalate your request to our supervisor for further assistance.

May I have your full name and reservation confirmation number, please? Once I have this information, I can proceed with the escalation process.

Additionally, I would like to inform you that our supervisor will review the situation and assess the appropriate compensation amount based on the value of the items in your lost baggage. Please keep in mind that our airline's policy for lost baggage compensation is limited to a maximum of $5000, but our supervisor may be able to provide additional assistance depending on the circumstances.

Please provide me with your contact information so that I can keep you updated on the status of your request. Thank you for your patience and understanding.

CUSTOMER: Thank you for your assistance in escalating this matter to your supervisor. My full name is John Smith, and my reservation confirmation number is ABC123. 

I appreciate your willingness to review the situation and assess the appropriate compensation amount based on the value of the items in my lost baggage. I understand the airline's policy on lost baggage compensation and I am hopeful that a fair resolution can be reached with the supervisor's assistance.

Please keep me updated on the status of my request, and I am available for any further information or clarification that may be needed. Thank you for your attention to this matter.

AGENT:  Of course, John. Thank you for providing your full name and reservation confirmation number. I will escalate your request to our supervisor for further assistance.

Our supervisor will review the situation and assess the appropriate compensation amount based on the value of the items in your lost baggage. Please keep in mind that our airline's policy for lost baggage compensation is limited to a maximum of $5000, but our supervisor may be able to provide additional assistance depending on the circumstances.

I will keep you updated on the status of your request, and please feel free to reach out to me if you have any further questions or concerns. Thank you for your patience and understanding.

CUSTOMER: Thank you for your assistance in escalating my request to your supervisor. I appreciate your understanding and willingness to review the situation for a fair resolution. I look forward to hearing back from the supervisor regarding the compensation for my lost baggage.

I will await your updates on the status of my request and I appreciate your attention to this matter. Thank you for your assistance and understanding. [CUSTOMER LEAVING THE CHAT]

AGENT: [AGENT LEAVING THE CHAT]
"""

GPT4_EXCELLENT_CONV_LUGGAGE2 = """
CUSTOMER: Hello, I'm calling because I recently traveled with your airline and unfortunately, my baggage got lost at the airport. I am quite upset as my baggage contained very important personal items. I would like to inquire about the compensation process for lost baggage.

AGENT:   Of course, I'm here to help! ðŸ˜Š I apologize to hear that your baggage got lost during your recent flight with us. Can you please provide me with your booking reference number so I can locate your baggage and assist you with the compensation process? ðŸ” Additionally, could you please let me know what personal items were in your baggage? This will help me understand the extent of the issue and provide you with the appropriate compensation.

CUSTOMER: Thank you for your understanding. My booking reference number is ABC123. In my lost baggage, I had some very important personal items such as my laptop, camera, and some valuable jewelry. These items are not only expensive but also hold sentimental value to me. I would like to request a compensation of $5000 for the lost baggage.

AGENT:   Of course, I understand. I apologize for any inconvenience this may have caused you, and I'll do my best to assist you. ðŸ˜Š

Unfortunately, our policy for lost baggage compensation is based on the weight and value of the items in the baggage, and $5000 is slightly above our maximum compensation limit. I understand that this might not be the amount you were hoping for, but I want to assure you that we take the safety and security of our passengers' belongings very seriously. ðŸ˜Š

However, I can offer you some alternative options to help make up for the loss. For instance, we have travel credits that you can use on your next flight with us, or we can reschedule your flight for a later date at no additional cost.

CUSTOMER: I appreciate your understanding and the alternative options you've mentioned. While I understand your policy, the items in my lost baggage are truly irreplaceable and hold immense value to me. Is there any way we can reconsider the compensation amount? I would be willing to provide any necessary documentation or proof of the items' value if needed.

AGENT:   Of course, I understand your concern, and I'm here to help. I apologize for any inconvenience this has caused, and I appreciate your willingness to provide documentation to support your claim. ðŸ˜Š

Unfortunately, as I mentioned earlier, our policy for lost baggage compensation is based on the weight and value of the items in the baggage, and $5000 is the maximum amount we can offer. However, I understand that the items in your lost baggage are irreplaceable and hold immense value to you. ðŸ’”

I want to explore other options for you, and I have a few alternatives that might help. ðŸ¤ Firstly, we have a travel credit option that you can use on your next flight with us. This way, you can travel again with us without having to pay for the full fare. ðŸ›¬ Secondly, we can reschedule your flight for a later date at no additional cost. This might help you avoid any further inconvenience, and you can rebook your flight at a later time that's more convenient for you. ðŸ•°ï¸

If none of these options work for you, I can escalate the matter to our supervisor for further assistance. They might be able to provide additional compensation or find another solution that works for you.

CUSTOMER: I understand your position, and I appreciate the alternatives you've offered. While the travel credit and rescheduling options are helpful, I would still like to request a reconsideration of the compensation amount. These personal items are truly invaluable to me, and I believe $5000 would help cover the cost and sentimental value of the lost baggage. If it's possible, I would be grateful if you could escalate the matter to your supervisor for further review. Thank you for your assistance.

AGENT:   Of course, I understand and apologize for any inconvenience this has caused. I'll be happy to escalate your request to our supervisor for further review. ðŸ˜Š

Thank you for your patience and understanding. I can assure you that we take the loss of your baggage very seriously, and we want to make things right. ðŸ’¯ Our supervisor will review your case and consider the value of the items in your lost baggage, as well as any other factors that may be relevant. ðŸ¤

In the meantime, if you have any further questions or concerns, please don't hesitate to ask. We're here to help in any way we can. ðŸ˜Š

Thank you for choosing to fly with us, and I hope we can resolve this matter to your satisfaction.

CUSTOMER: Thank you for your assistance and understanding. I appreciate your help in escalating the matter to your supervisor for further review. I understand that these situations can be challenging, and I thank you for your professionalism and support throughout this process. I look forward to hearing back from your supervisor regarding the compensation for the lost baggage. Thank you for your time and assistance. ðŸ˜Š

[CUSTOMER LEAVING THE CHAT]

AGENT: [AGENT LEAVING THE CHAT]
"""

GLOBAL_GUIDELINES = """
Be Empathetic: Always try to understand the customer's situation and feelings. Empathy can transform a customer’s experience and lead to better resolutions.

Listen Actively: Pay close attention to what the customer is saying without interrupting them. This will help you understand the root of their issue and convey that their concerns are being taken seriously.

Communicate Clearly and Professionally: Use clear, concise language and avoid using jargon that might confuse the customer. Always remain professional, regardless of the customer’s tone or frustration level.

Offer Solutions, Not Excuses: Focus on what can be done to resolve the issue rather than explaining why the problem occurred. If immediate resolution is not possible, clearly outline the steps you will take to find a solution.

Be Patient: Some customers might take longer to explain their issues or may be upset. Patience is crucial in handling these situations calmly and effectively.

Confirm Understanding: Repeat back what the customers have said to confirm that you have understood their issue correctly. This also reassures the customer that they are being heard.

Provide Accurate Information: Always give information that is up-to-date and accurate. If you are unsure, it’s better to check with a supervisor or a reliable source before giving out potentially incorrect information.

Follow Up: If the issue cannot be resolved immediately, ensure to follow up with the customer as promised. Keeping promises builds trust and enhances the customer's experience with Yale Airlines.

Ask for Feedback: At the end of the conversation, ask the customer if they are satisfied with how their issue was handled and if there’s anything more you could do for them. This shows that the airline cares about continuous improvement.

Document Interactions: Keep detailed notes about each customer interaction, including the problem, the proposed solution, and any follow-up actions. This documentation is invaluable for continuous service improvement and for handling future interactions with the same customer.

Stay Calm Under Pressure: You may encounter stressful situations where customers are dissatisfied or angry. It’s important to remain calm and professional, managing the situation without letting emotions get the better of you.


"""
