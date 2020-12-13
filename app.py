import os
# Use the package we installed
import logging
import random

from slack_bolt import App, Say, BoltContext
from slack_sdk import WebClient

logging.basicConfig(level=logging.DEBUG)

# creating some hard coded tips
tips = [
    "Always make sure that you update the Request URL when restarting ngrok",
    "Make sure you check your scopes when an API method does not work",
    "Every API call has a scope check that you use the correct ones and when calling something new add that scope on Slack",
    "After changing the scope you need to install your App again",
    "Every Event you want to use, you need to subscribe to on Slack",
    "Every Slack command needs the Request URL",
    "The Bot token is on the Basics Page",
    "The Slack Signing Secret is on the OAuth & Permission page",
    "Limit the scopes to what you really need",
    "You can add collaborators to your Slack App under Collaborators, they need to be in the workspace",
    "To use buttons you need to enable Interactive Components",
    "Always go in tiny steps, use the logger or print statements to see where you are and if events reach your app",
    "If the user does something on Slack always send a response, even if it is just an emoji",
    "Your App can use on the users behalf, you need to get User Scopes in that case. Later this would lead to having to save user tokes",
    "Do not plan to much, do simple things first, when you get these done then start to dream big",
    "Storing persistent data in a DB makes sense, when you are not familiar with it maybe a dict in a file might be enough for now",
    "Oauth -- so authenticating the app and user is important when distributing your app, while locally developing it is not that important yet, get some functionality going first",
    "Have the Slack API, Slack Events and your Slack Build App page open in your browser to have fast access",
    "Slash commands need to be unique in a workspace, so do append your bots name to them"
]

#Hard codes some scenarios the Goblin does once you @ him
come_hither = [
    f"GAH!!! Does Ticket Goblin get more tickets today, ",
    '*You hear frantic tiny footsteps getting louder* *Panting* Did anyone... *Gasps* have precious ticketses?',
    '*You hear frantic tiny footsteps getting louder* GIMME YOUR TICKETSES', 
    '*A faint voice starts to emerge...from above?!*\n\*Crashing through the ceiling, Ticket Goblin holds out his hand*\nDo you oblige him with a ticket for your troubles?',
    f'\*With small voice and meek appearance, Ticket Goblin asks* "Does you have a ticketses for Goblin?"',
    '*A swoosh, a sparkle, and a swirl, Ticket Goblin appears before you* "Please hands over your trouble ticketses"',
    "I hear ya need some help, and these ticketses may be just what ya need!"
]


# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# This reacts to you calling the bot
# it just prints a message and says something back to you in the channel where you call it
# and in a specified channel "hellothere"


@app.event("app_mention")
def event_test(body, event, say, logger, client):
    logger.info(event)
   #say(f"Gah!<@{body['event']['user']}>! What can Ticket Goblin do for you!?")
    GoblinCall = random.choice(come_hither);
    block =  [
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": GoblinCall
				}
			]
		},
        {
			"type": "divider"
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Yup!",
						"emoji": True
					},
					"style": "primary",
					"value": "click_me_123"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": True,
						"text": "Ew, No"
					},
					"style": "danger",
					"value": "click_me_123"
				}
			]
		}
	]
    
    client.chat_postEphemeral(channel=event['channel'], user=event['user'], text=f"GAH!!! Does Ticket Goblin get more tickets today, <@{body['event']['user']}>!?", blocks=block)

# whenever a member joins a channel they are asked to introduce themselves with buttons
# this would be better if it only happens when a specific channel is joined e.g. the new hackathon channel
# or an intro channel. Maybe you want to try that
@app.event("member_joined_channel")
def event_join(body, say, logger, client):
    text = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Hello <@{body['event']['user']}>,\n would you like to introduce yourself a bit? "
            },
            "accessory": {
                "type": "image",
                "image_url": "https://api.slack.com/img/blocks/bkb_template_images/approvalsNewDevice.png",
                "alt_text": "computer thumbnail"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "YES"
                    },
                    "action_id": "intro_yes_button",
                    "style": "primary",
                    "value": "yes"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "nope"
                    },
                    "action_id": "intro_nope_button",
                    "style": "danger",
                    "value": "nope"
                }
            ]
        }
    ]
    client.chat_postMessage(
        channel=body['event']['channel'], user=body['event']['user'], blocks=text)

# Implementing the yes button which opens a model which the user can fill out and then overwrites
# the original message


@app.action("intro_yes_button")
def yes_button(body, action, logger, client, ack):
    ack()

    ## triggering a modal view
    res = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "intro_modal",
            "title": {"type": "plain_text", "text": "My Intro",},
            "submit": {"type": "plain_text", "text": "Submit",}, # has a submit button is optional, that submit will trigger callback_id
            "close": {"type": "plain_text", "text": "Cancel",},
            "private_metadata": f"{body['channel']['id']},{body['message']['ts']}", ## stored so we can update the original message
            "blocks": [ ## create 4 input fields
                {
                    "type": "input",
                    "block_id":"where",
                    "element": {"type": "plain_text_input", "action_id": "where"},
                    "label": {"type": "plain_text", "text": "Where are you from?",},
                },
                {
                    "type": "input",
                    "block_id":"you",
                    "element": {"type": "plain_text_input", "action_id": "you"},
                    "label": {"type": "plain_text", "text": "Tell us about yourself",},
                },
                {
                    "type": "input",
                    "block_id":"learn",
                    "element": {"type": "plain_text_input", "action_id": "learn"},
                    "label": {"type": "plain_text", "text": "What do you want to learn",},
                },
                {
                    "type": "input",
                    "block_id":"project",
                    "element": {"type": "plain_text_input", "action_id": "project"},
                    "label": {"type": "plain_text", "text": "What project would you like to work on?",},
                }
            ],
        },
    )


    logger.info(res)

### reads out our simple modal and formats the result a bit
@app.view('intro_modal')
def intro_modal_submitted(body, ack, logger, client):
	ack()
	logger.info("Modal Submitted")

	## reading the data from the input fields
	you = body['view']['state']['values']['you']['you']['value']
	learn = body['view']['state']['values']['learn']['learn']['value']
	where = body['view']['state']['values']['where']['where']['value']
	project = body['view']['state']['values']['project']['project']['value']

	# reading metadata from the original channel and ts that was added 
	data = body['view']['private_metadata'].split(',')
	block = [
		        {
		            "type": "section",
		            "text": {
		                "type": "mrkdwn",
		                "text": f"<@{body['user']['id']}> INTRO"
		            }
		        },
		        {
		            "type": "section",
		            "text": {
		                "type": "mrkdwn",
		                "text": f"*From:* \n {where}"
		            }
		        },
		        {
		            "type": "section",
		            "text": {
		                "type": "mrkdwn",
		                "text": f"*Who I am:* \n {you}"
		            }
		        },
		        {
		            "type": "section",
		            "text": {
		                "type": "mrkdwn",
		                "text": f"*What I want to learn:* \n {learn}"
		            }
		        },
		        {
		            "type": "section",
		            "text": {
		                "type": "mrkdwn",
		                "text": f"*What I want to work on:* \n {project}"
		            }
		        }
	        ]
	client.chat_update(channel=data[0],
                       ts=data[1], blocks=block)

# print shame on you when they do not want to introduce themselves
@app.action("intro_nope_button")
def yes_button(body, action, logger, client, ack):
    ack()

    # creating a new message which has parts of the old messag and adds a section
    oldMessage = [body['message']['blocks'][0]]
    oldMessage.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"You said nope, SHAME on you!"
        }
    })

    # we are updating an existing message here and remove the buttons
    client.chat_update(channel=body['channel']['id'],
                       ts=body['message']['ts'], blocks=oldMessage)

# waits for slash command, if command comes checks if it has arguments
# if not prints a tip if arguments adds a new tip


@app.command("/py_tips")
def joke_called(body, command, logger, client, ack):
    ack()
    logger.info("In py tip")

    # check if the user wants a tip or added a new tip
    if not checkKey(command, 'text'):
        block = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":tada: <@{command['user_id']}> you asked for a tip, here you go:"
            }
        }
        ]
        attach = [
            {
                "color": "#f26744",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{random.choice(tips)}"
                        }
                    }
                ]
            }
        ]
        client.chat_postMessage(
            channel=command['channel_id'], blocks=block, attachments=attach)

    else:  # we are adding a tip

        # these tips will get deleted when the bot restarts
        tips.append(command['text'])
        # so a DB or at least saving things to file makes sense

        # create a section block with a text to the user
        block = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":tada: <@{command['user_id']}> you added a new tip, good for you!"
            }
        }
        ]
        # creates an attachment which then has a color bar
        attach = [
            {
                "color": "#f6c766",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{command['text']}"
                        }
                    }
                ]
            }
        ]

        client.chat_postMessage(
            channel=command['channel_id'], blocks=block, attachments=attach)

        # this would post only to that user and not publicly
        #client.chat_postEphemeral(channel=command['channel_id'], user=command['user_id'], blocks=block, attachments=attach);


def checkKey(dict, key):

    if key in dict.keys():
        return True
    else:
        return False


# With this you can create a simple App home
# You need to go to App home on Slack and enable App home so that you can listen to this event

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:

        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id = event["user"],
            # the view object that appears in the app home
            view = {
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to your _App's Home_* :tada:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "action_id": "HelloThere",
                                "type": "button",
                                "style": "primary",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Click me now!"
                                }
                            },
                            {
                                # this button is not implemented you can implement it in the same was as HelloThere
                                "action_id": "whythere2",
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Click me now2!"
                                }
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

# Example button for button on App home which just posts a message to the user in the
# apps user channel
@app.action("HelloThere")
def react_to_button(body, logger, client):
    logger.info(body)
    client.chat_postMessage(
        channel=body["user"]["id"], text="You pushed a button!")

# Not used in our app, to use it you would need to subscribe to the message.channels event
# to bot then listens to all public messages and replies if you write "test"

# @app.message("test")
# def reply_to_test(say):
#     say("Yes, tests are important!")

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
