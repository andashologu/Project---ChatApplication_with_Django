# How online-offline Status 

User1 sends a message
       |
       v
[Message echoes back to User1]
       |
       v
[Message sent to Recipient]
       |
       +--- Recipient is offline? ---> [Message stored as "Sent"]
       |                                (Message awaits delivery)
       |
       +--- Recipient is online?
                 |
                 +--- Has the chat been viewed?
                         |   
                         +--- Yes ---> [Message marked as "Read"]
                         |                (Unread count set to 0)
                         |
                         +--- No  ---> [Message marked as "Delivered"]
                                           (Unread count increases)
