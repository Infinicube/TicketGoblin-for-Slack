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
    '*You hear frantic tiny footsteps getting louder* *Panting* \nDid anyone... *Gasps* have precious ticketses?',
    '*You hear frantic tiny footsteps getting louder* \nGIMME YOUR TICKETSES', 
    '*A faint voice starts to emerge...from above?!*\n*Crashing through the ceiling, Ticket Goblin holds out his hand*\nDo you oblige him with a ticket for your troubles?',
    f'*With small voice and meek appearance, Ticket Goblin asks* \n"Does you have a ticketses for Goblin?"',
    '*A swoosh, a sparkle, and a swirl, Ticket Goblin appears before you* \n"Please hands over your trouble ticketses"',
    "I hear ya need some help, and these ticketses may be just what ya need!"
]

#Hard codes for some sad responses if rejected
sadness = [
    "Dejected, Ticket Goblin looks at you sheepishly as he returns to his garbage can",
    "Ticket Goblin screams and runs out of the door",
    "Ticket Goblin winces when you tell him 'no'. You should feel bad, but you don't.",
    "Ticket Goblin simply vanishes from sight, to a dimension none could fathom"
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
					"value": "click_me_123",
                    "action_id": "needs_help"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"emoji": True,
						"text": "Ew, No"
					},
					"style": "danger",
					"value": "click_me_123",
                    "action_id": "no_help"
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
                "text": f"Hello <@{body['event']['user']}>,\n are you in need of assistance? "
            },
            "accessory": {
                "type": "image",
                "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTi4nI9nIPz6vcSdN0-D394G4almS-5YmrNGA&usqp=CAU",
                "alt_text": "tiny gob"
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
                    "action_id": "needs_help",
                    "style": "primary",
                    "value": "yes"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "nope"
                    },
                    "action_id": "no_help",
                    "style": "danger",
                    "value": "nope"
                }
            ]
        }
    ]
    client.chat_postMessage(
        channel=body['event']['channel'], user=body['event']['user'], blocks=text)

# Implementing the yes button which opens a model which the user can fill out and submit into a queue
@app.action("needs_help")
def yes_button(body, action, logger, client, ack):
    ack()
    print("Hi")

    ## triggering a modal view
    res = client.views_open(
         trigger_id=body["trigger_id"],
         view={
	"type": "modal",
	"submit": {
		"type": "plain_text",
		"text": "Submit",
		"emoji": True
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
		"emoji": True
	},
	"title": {
		"type": "plain_text",
		"text": "Ticket app",
		"emoji": True
	},
	"blocks": [
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "Awaiting Release"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/task-icon.png",
					"alt_text": "Task Icon"
				},
				{
					"type": "mrkdwn",
					"text": "Task"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_1.png",
					"alt_text": "Michael Scott"
				},
				{
					"type": "mrkdwn",
					"text": "<fakelink.toUser.com|Michael Scott>"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*<fakelink.com|WEB-1098 Adjust borders on homepage graphic>*"
			},
			"accessory": {
				"type": "overflow",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": ":white_check_mark: Mark as done",
							"emoji": True
						},
						"value": "done"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":pencil: Edit",
							"emoji": True
						},
						"value": "edit"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":x: Delete",
							"emoji": True
						},
						"value": "delete"
					}
				]
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "Open"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/newfeature.png",
					"alt_text": "New Feature Icon"
				},
				{
					"type": "mrkdwn",
					"text": "New Feature"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_2.png",
					"alt_text": "Pam Beasely"
				},
				{
					"type": "mrkdwn",
					"text": "<fakelink.toUser.com|Pam Beasely>"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*<fakelink.com|MOB-2011 Deep-link from web search results to product page>*"
			},
			"accessory": {
				"type": "overflow",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": ":white_check_mark: Mark as done",
							"emoji": True
						},
						"value": "done"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":pencil: Edit",
							"emoji": True
						},
						"value": "edit"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":x: Delete",
							"emoji": True
						},
						"value": "delete"
					}
				]
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "Awaiting Release"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/task-icon.png",
					"alt_text": "Task Icon"
				},
				{
					"type": "mrkdwn",
					"text": "Task"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_1.png",
					"alt_text": "Michael Scott"
				},
				{
					"type": "mrkdwn",
					"text": "<fakelink.toUser.com|Michael Scott>"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*<fakelink.com|WEB-1098 Adjust borders on homepage graphic>*"
			},
			"accessory": {
				"type": "overflow",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": ":white_check_mark: Mark as done",
							"emoji": True
						},
						"value": "done"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":pencil: Edit",
							"emoji": True
						},
						"value": "edit"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":x: Delete",
							"emoji": True
						},
						"value": "delete"
					}
				]
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/mediumpriority.png",
					"alt_text": "palm tree"
				},
				{
					"type": "mrkdwn",
					"text": "*Medium Priority*"
				}
			]
		},
		{
			"type": "divider"
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "Open"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/newfeature.png",
					"alt_text": "New Feature Icon"
				},
				{
					"type": "mrkdwn",
					"text": "New Feature"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_2.png",
					"alt_text": "Pam Beasely"
				},
				{
					"type": "mrkdwn",
					"text": "<fakelink.toUser.com|Pam Beasely>"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*<fakelink.com|MOB-2011 Deep-link from web search results to product page>*"
			},
			"accessory": {
				"type": "overflow",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": ":white_check_mark: Mark as done",
							"emoji": True
						},
						"value": "done"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":pencil: Edit",
							"emoji": True
						},
						"value": "edit"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":x: Delete",
							"emoji": True
						},
						"value": "delete"
					}
				]
			}
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "mrkdwn",
					"text": "Awaiting Release"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/task-icon.png",
					"alt_text": "Task Icon"
				},
				{
					"type": "mrkdwn",
					"text": "Task"
				},
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/profile_1.png",
					"alt_text": "Michael Scott"
				},
				{
					"type": "mrkdwn",
					"text": "<fakelink.toUser.com|Michael Scott>"
				}
			]
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*<fakelink.com|WEB-1098 Adjust borders on homepage graphic>*"
			},
			"accessory": {
				"type": "overflow",
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": ":white_check_mark: Mark as done",
							"emoji": True
						},
						"value": "done"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":pencil: Edit",
							"emoji": True
						},
						"value": "edit"
					},
					{
						"text": {
							"type": "plain_text",
							"text": ":x: Delete",
							"emoji": True
						},
						"value": "delete"
					}
				]
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "context",
			"elements": [
				{
					"type": "image",
					"image_url": "https://api.slack.com/img/blocks/bkb_template_images/highpriority.png",
					"alt_text": "High Priority"
				},
				{
					"type": "mrkdwn",
					"text": "*High Priority*"
				}
			]
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Pick a ticket list from the dropdown"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item",
					"emoji": True
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "All Tickets",
							"emoji": True
						},
						"value": "all_tickets"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Assigned To Me",
							"emoji": True
						},
						"value": "assigned_to_me"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Issued By Me",
							"emoji": True
						},
						"value": "issued_by_me"
					}
				],
				"initial_option": {
					"text": {
						"type": "plain_text",
						"text": "Assigned To Me",
						"emoji": True
					},
					"value": "assigned_to_me"
				}
			}
		}
	]
},
)


    logger.info(res)

### A sad response is made from Ticket Goblin if denied
@app.action("no_help")
def no_button(body, event, action, logger, client, ack):
    ack()
    sad = random.choice(sadness);
    block =  [
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": sad
				}
			]
		}
    ]
    #print(sad)
    #client.chat_postEphemeral(channel=event['channel'], user=event['user'], blocks=block)   

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
