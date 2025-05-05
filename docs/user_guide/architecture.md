This guide shows how to use *NextGen UI Agent* in your Project/Application/AI assistant.

In short, *UI Agent* takes `User Prompt` and [`Structured Data`](./input_data.md) relevant to this prompt as an input, and generates `UI component` to visualize that piece of data to the user.

Your application, called *Controlling assistant*, has to load these structured data first, before calling the *UI Agent*. It can do it directly, for example using `LLM Tools Calling`, or it can call *Data providing agent* in case of Multi-Agent architecture.

*UI Agent* core works with abstract representation of the `UI component`, which can be rendered using pluggable UI component system renderers (**ToDo** link to the relevant chapter), and integrated into the GUI frontend of the *Controlling assistant*.

*Controlling assistant* can also generate *Natural language response* based on this data and deliver it to the user through GUI frontend or Voice. 
To follow vision of the **NextGen UI**, this natural language response should not repeat visualized data, but rather provide data summarizations, insights based on the data, proposals of the user actions, etc. 
*UI Agent* itself has nothing to do with this response.


*UI Agent* can be integrated into *Controlling Assistant* developed using distinct AI frameworks (**ToDo** link to the relevant chapter).


