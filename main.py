"""
Module: GameGeneratorApp
Description: iOS/iPadOS app (to be created via kivy-ios) that allows the user to create and play
  AI generated games.  User must provide a valid xAI Grok API key.  Enter a prompt in the provided
  TextInput, useful prompt prefixes and suffixes are provided to help Grok generate useful output.
  Tap the generate code button to make a request to Grok API and return game code per your request
  as a kivy widget written in python.  Returned code can be modified as needed/desired by the user
  if they have a working knowledge of python/kivy.  Tap the run button to execute the code and play
  your game.
Author: Ben Bargabus
Date: May 15, 2025
Version: 1.0.0
License: CC BY-NC
Dependencies: kivy
"""

"""
Notes: This was created as a quick and dirty (emphasis on very quick and very dirty) proof of 
concept that frontier LLMs (specifically Grok by xAI but this could be adapted to others with
ease) could be use to generate playable games on iOS and iPadOS.  I did this to prove the concept
of "AI first" games that would be playable on the dominant mobile platforms in the US from both
a technical perspective and the perspective of compliance with app store submission rules.

The user interface is terrible, that wasn't the point here.  The code is sloppy too.  Again, not 
point.  This is functional though in the sense that it allows the user to enter a prompt, calls
the Grok API, returns the response (code) and allows the user to edit/improve it, then allows the
user to run the code as a kivy widget to play their game.

The choice to go with kivy here was made to provide a mechanism to execute arbitrary source code 
at run time.  Apple has a product that does something similar with Swift, Swift Playgrounds, but
to my knowledge there's no mechanism for third party apps to do anything similar with Swift.  There
are iOS/iPadOS app based IDEs and these are allowed in the app store provided the user has the 
ability to view and edit the code that will be executed (e.g. Pythonista) so in theory this app
would be equally viable given the code is displayed and the user can edit.  To make AI-first mobile
gaming a reality for the (non-coder) masses would require going directly from prompt to play which 
would necessitate changes in Apple App Store policies and likely a new (highly complex) method to
validate said code before execution.

I've found that some prompt engineering can help Grok to produce more viable results and I've 
included a "prefix" and "suffix" that will be appended to the prompt that guide Grok on language, 
use of kivy, some guidance on inputs, etc...  That said, much of the initial responses from Grok 
are not viable without human intervention.  For a programmer the fixes are generally very easy, 
for non-programmers this becomes a big obstacle.  Groks capabilities and accuracy have increased 
greatly over time though and I expect we'll reach a point where responses can be used in most cases
without any modification by the user.

To allow anyone exploring this proof of concept to do so with minimal effort I have set a working 
game into the code Text Input.  This will allow you to run a game without actually requesting new
code from Grok via the API.  If you wish to request your own game code from Grok you'll need to 
provide an xAI Grok API key (sorry, I'm not subsidizing your tokens :-) ) to do so.  It would be 
great if ultimately xAI provided a mechanism such as OAuth for Supergrok and X Premium+ subscribers
to generate API keys as well and make API calls without purchasing additional tokens. For the time
being this is the system we have though.  Tokens at the individual level are cheap, providing them
to the world requires a revenue model and this app doesn't currently support that in my mind.
If you do generate your own code via API call I'd recommend testing the resulting code in your 
Python IDE of choice to debug it rather than doing so directly in this app if you do.  Easier to 
debug and address any issues that way.

This is available to anyone under the Creative Commons BY-NC license.  Feel free to beat it up
or extend it as you wish for non-commercial purposes as long as you provide attribution to me. 
If I were to take this further I would definitely clean up the UI/UX, I would split error/debug 
feedback into a separate text box from the generated code (failures overwrite code as it is), and 
provide a mechanism to save and retrieve completed games.  There's much more to be done beyond that
but just those few changes would make for something more complete than a proof of concept.

If you do extend this I'd love to hear from you.

How to build: This requires kivy-ios to create an Xcode project and then Xcode to complete the 
iOS app.  Steps:

1) make sure you have all dependencies for kivy-ios in place (e.g. automake, autoconf, see kivy-ios documentation)
2) clone the latest kivy-ios from GitHub, follow instructions to build python3 and kivy recipes
3) use kivy-ios's toolchain to create the Xcode project (toolchain create GenerateGameAIApp /path/to/this/main.py)
3) open the resulting Xcode project into Xcode
4) build the project
"""

# Import necessary Kivy modules for building the app
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.network.urlrequest import UrlRequest
# Import json for handling API data
import json

# Define the main application class inheriting from Kivy App
class GameGeneratorApp(App):
    # Build the main UI layout
    def build(self):
        # Create a vertical BoxLayout with padding and spacing
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Create input field for Grok API key
        self.api_key_input = TextInput(hint_text='Enter your Grok API key', multiline=False, size_hint=(1, 0.1))
        self.layout.add_widget(self.api_key_input)

        # Create input field for prompt prefix with default Kivy game instructions
        self.prefix_input = TextInput(hint_text='Prompt prefix (optional)', multiline=True, size_hint=(1, 0.1), text="I want you to write me code in python utilizing Kivy.  This should be constructed as a single file, not relying on multiple python source files or external files such as sprites.  It should contain a Kivy compatible Widget named GeneratedGameWidget.  This will be targeted to run on iPhones and iPads running recent releases of iOS and iPadOS.  It should make use of touch controls with fallbacks for iOS and iPadOS supported game controllers and keyboards.  Pay close attention to coordinate systems and positioning to make sure orientation of various entities within the resulting product behave as intended.  Now, following these instructions produce the following game for me: \n\n")
        self.layout.add_widget(self.prefix_input)

        # Create input field for prompt suffix
        self.suffix_input = TextInput(hint_text='Prompt suffix (optional)', multiline=True, size_hint=(1, 0.1), text="\n\nReturn only the generated code as your response, do not include any additional text or information.")
        self.layout.add_widget(self.suffix_input)

        # Create input field for the game prompt
        self.prompt_input = TextInput(hint_text='Enter your game prompt', multiline=True, size_hint=(1, 0.3))
        self.layout.add_widget(self.prompt_input)

        # Create button to generate game code
        generate_btn = Button(text='Generate Game Code', size_hint=(1, 0.1))
        generate_btn.bind(on_press=self.generate_code)
        self.layout.add_widget(generate_btn)

        # Define default Asteroids game code as a string
        asteroids_code = """from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Triangle, PushMatrix, PopMatrix, Rotate
from kivy.utils import platform
from random import randint, uniform
import math

try:
    from pyobjus import autoclass
    GCController = autoclass('GCController')
    GCGamepad = autoclass('GCGamepad')
    GCExtendedGamepad = autoclass('GCExtendedGamepad')
except ImportError:
    GCController = None
    GCGamepad = None
    GCExtendedGamepad = None

Window.size = (800, 600)

class Spaceship(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Spaceship, self).__init__(**kwargs)
        self.size = (40, 40)
        with self.canvas:
            PushMatrix()
            self.rotation = Rotate(angle=self.angle, origin=self.center)
            Color(1, 1, 1, 1)
            self.triangle = Triangle(points=[0, 0, 0, 0, 0, 0])
            PopMatrix()
        self.bind(pos=self.update_graphics, size=self.update_graphics, angle=self.update_graphics)

    def update_graphics(self, *args):
        center_x, center_y = self.center
        self.rotation.angle = self.angle - 90  # 0° points up
        self.rotation.origin = self.center
        self.triangle.points = [
            center_x, center_y + self.height * 0.6,           # Nose (forward)
            center_x - self.width * 0.5, center_y - self.height * 0.4,  # Left rear
            center_x + self.width * 0.5, center_y - self.height * 0.4   # Right rear
        ]

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        if self.x < 0:
            self.x = Window.width
        if self.x > Window.width:
            self.x = 0
        if self.y < 0:
            self.y = Window.height
        if self.y > Window.height:
            self.y = 0

    def rotate(self, direction):
        self.angle += direction * 5

    def thrust(self):
        angle_rad = math.radians(self.angle)
        thrust_vector = Vector(math.cos(angle_rad), math.sin(angle_rad)) * 0.2
        self.velocity = Vector(*self.velocity) + thrust_vector

    def shoot(self, parent):
        bullet = Bullet()
        angle_rad = math.radians(self.angle)
        nose_x = self.center_x + math.cos(angle_rad) * self.height * 0.6
        nose_y = self.center_y + math.sin(angle_rad) * self.height * 0.6
        bullet.pos = (nose_x - bullet.size[0]/2, nose_y - bullet.size[1]/2)
        bullet.velocity = Vector(math.cos(angle_rad), math.sin(angle_rad)) * 25
        parent.add_widget(bullet)
        parent.bullets.append(bullet)

class Bullet(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    lifetime = NumericProperty(10.0)

    def __init__(self, **kwargs):
        super(Bullet, self).__init__(**kwargs)
        self.size = (5, 5)
        with self.canvas:
            Color(1, 1, 1, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics)

    def update_graphics(self, *args):
        self.ellipse.pos = self.pos

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class Asteroid(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    size_level = NumericProperty(3)  # 3=large, 2=medium, 1=small

    def __init__(self, size_level=3, **kwargs):
        super(Asteroid, self).__init__(**kwargs)
        self.size_level = size_level
        self.size = (40 * size_level, 40 * size_level)
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics)

    def update_graphics(self, *args):
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        if self.x < 0:
            self.x = Window.width
        if self.x > Window.width:
            self.x = 0
        if self.y < 0:
            self.y = Window.height
        if self.y > Window.height:
            self.y = 0

    def split(self, parent):
        if self.size_level > 1:
            for _ in range(2):
                new_asteroid = Asteroid(size_level=self.size_level - 1)
                new_asteroid.pos = (self.x + randint(-10, 10), self.y + randint(-10, 10))
                new_asteroid.velocity = Vector(uniform(-2, 2), uniform(-2, 2))
                parent.asteroids.append(new_asteroid)
                parent.add_widget(new_asteroid)

class FireButton(Widget):
    def __init__(self, **kwargs):
        super(FireButton, self).__init__(**kwargs)
        self.size = (80, 80)
        self.pos = (Window.width - 100, 20)
        with self.canvas:
            Color(1, 0, 0, 0.5)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics)

    def update_graphics(self, *args):
        self.ellipse.pos = self.pos

    def collide_point(self, x, y):
        cx, cy = self.center
        radius = self.width / 2
        return math.sqrt((x - cx)**2 + (y - cy)**2) <= radius

class GeneratedGameWidget(Widget):
    spaceship = ObjectProperty(None)
    score = NumericProperty(0)
    lives = NumericProperty(3)
    game_state = StringProperty('playing')

    def __init__(self, **kwargs):
        super(GeneratedGameWidget, self).__init__(**kwargs)
        self.asteroids = []
        self.bullets = []
        self.spaceship = Spaceship()
        self.spaceship.center = self.center
        self.add_widget(self.spaceship)

        self.score_label = Label(text=f'Score: {self.score}', pos=(20, Window.height - 80))
        self.lives_label = Label(text=f'Lives: {self.lives}', pos=(20, Window.height - 110))
        self.game_over_label = Label(text='Game Over\\nTap to Restart', center=self.center,
                                   font_size=40, opacity=0)
        self.fire_button = FireButton()
        self.add_widget(self.score_label)
        self.add_widget(self.lives_label)
        self.add_widget(self.game_over_label)
        self.add_widget(self.fire_button)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._onKeyboardDown)
        self._keyboard.bind(on_key_up=self._onKeyboardUp)
        self.keys_pressed = set()
        self.touch_pos = None
        self.controllers = []
        self.touch_ids = []
        self.fire_touch_id = None

        self.GCController = GCController
        self.GCGamepad = GCGamepad
        self.GCExtendedGamepad = GCExtendedGamepad
        if self.GCController:
            controllers = self.GCController.controllers()
            if controllers and controllers.count() > 0:
                self.check_controllers()

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._onKeyboardDown)
        self._keyboard.unbind(on_key_up=self._onKeyboardUp)
        self._keyboard = None

    def _onKeyboardDown(self, keyboard, keycode, text, modifiers):
        self.keys_pressed.add(keycode[1])
        if keycode[1] == 'spacebar' and self.game_state == 'playing':
            self.spaceship.shoot(self)
        return True

    def _onKeyboardUp(self, keyboard, keycode):
        if keycode[1] in self.keys_pressed:
            self.keys_pressed.remove(keycode[1])
        return True

    def on_touch_down(self, touch):
        if self.game_state == 'game_over':
            self.reset_game()
            return True
        if self.fire_button.collide_point(*touch.pos):
            self.spaceship.shoot(self)
            self.fire_touch_id = touch.uid
            return True
        if not self.touch_ids:
            self.touch_pos = touch.pos
            self.touch_ids.append(touch.uid)
        else:
            self.spaceship.shoot(self)
        return True

    def on_touch_move(self, touch):
        if touch.uid == self.touch_ids[0] if self.touch_ids else False:
            self.touch_pos = touch.pos
        return True

    def on_touch_up(self, touch):
        if touch.uid in self.touch_ids:
            self.touch_ids.remove(touch.uid)
            self.touch_pos = None
        if touch.uid == self.fire_touch_id:
            self.fire_touch_id = None
        return True

    def check_controllers(self):
        ignore_gamepad_input = False

        # Check the platform using kivy.utils.platform
        if platform == 'ios' and autoclass:
            try:
                # Use pyobjus to check if running in the iOS simulator
                UIDevice = autoclass('UIDevice')
                current_device = UIDevice.currentDevice()
                model = current_device.model  # e.g., "iPhone Simulator" or "iPhone"
                if 'Simulator' in model:
                    print("Running in iOS simulator")
                    ignore_gamepad_input = True
                else:
                    print("Running on a physical iOS device")
            except Exception as e:
                print(f"Error checking device: {e}")
                ignore_gamepad_input = True  # Fallback
        elif platform != 'ios':
            print(f"Running on {platform}, not iOS")
            ignore_gamepad_input = False  # Example behavior for non-iOS
        else:
            print("iOS detected, but pyobjus not available")
            ignore_gamepad_input = True  # Default if pyobjus isn’t installed
            
        if GCController and not ignore_gamepad_input:
            controllers = GCController.controllers()
            self.controllers = [controllers.objectAtIndex_(i) for i in range(controllers.count())]
            for controller in self.controllers:
                gamepad = controller.extendedGamepad or controller.gamepad
                if gamepad:
                    gamepad.valueChangedHandler = self.handle_gamepad_input
        else:
            # Handle other platforms if needed
            pass

    def handle_gamepad_input(self, gamepad, element):
        if element == gamepad.dpad:
            x_value = gamepad.dpad.xAxis.value
            if x_value > 0.5:
                self.spaceship.rotate(-1)
            elif x_value < -0.5:
                self.spaceship.rotate(1)
        elif element == gamepad.buttonA and gamepad.buttonA.isPressed:
            self.spaceship.thrust()
        elif element == gamepad.buttonX and gamepad.buttonX.isPressed:
            self.spaceship.shoot(self)

    def spawn_asteroid(self):
        side = randint(0, 3)
        if side == 0:  # Top
            pos = (randint(0, Window.width), Window.height + 50)
            velocity = Vector(uniform(-2, 2), uniform(-3, -1))
        elif side == 1:  # Right
            pos = (Window.width + 50, randint(0, Window.height))
            velocity = Vector(uniform(-3, -1), uniform(-2, 2))
        elif side == 2:  # Bottom
            pos = (randint(0, Window.width), -50)
            velocity = Vector(uniform(-2, 2), uniform(1, 3))
        else:  # Left
            pos = (-50, randint(0, Window.height))
            velocity = Vector(uniform(1, 3), uniform(-2, 2))
        asteroid = Asteroid(size_level=3)
        asteroid.pos = pos
        asteroid.velocity = velocity
        self.asteroids.append(asteroid)
        self.add_widget(asteroid)

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.game_state = 'playing'
        self.spaceship.center = self.center
        self.spaceship.velocity = [0, 0]
        self.spaceship.angle = 0
        self.remove_widget(self.spaceship)
        self.spaceship = Spaceship()
        self.spaceship.center = self.center
        self.add_widget(self.spaceship)
        for asteroid in self.asteroids[:]:
            self.remove_widget(asteroid)
        self.asteroids.clear()
        for bullet in self.bullets[:]:
            self.remove_widget(bullet)
        self.bullets.clear()
        self.game_over_label.opacity = 0

    def update(self, dt):
        if self.game_state != 'playing':
            return

        if self.controllers:
            for controller in self.controllers:
                gamepad = controller.extendedGamepad or controller.gamepad
                if gamepad:
                    x_value = gamepad.dpad.xAxis.value
                    if x_value > 0.5:
                        self.spaceship.rotate(-1)
                    elif x_value < -0.5:
                        self.spaceship.rotate(1)
                    if gamepad.buttonA.isPressed:
                        self.spaceship.thrust()
                    if gamepad.buttonX.isPressed:
                        self.spaceship.shoot(self)
        elif self.touch_pos:
            touch_x, touch_y = self.touch_pos
            ship_x, ship_y = self.spaceship.center
            angle = math.degrees(math.atan2(touch_y - ship_y, touch_x - ship_x))
            self.spaceship.angle = angle
            self.spaceship.thrust()
        else:
            if 'left' in self.keys_pressed:
                self.spaceship.rotate(1)
            if 'right' in self.keys_pressed:
                self.spaceship.rotate(-1)
            if 'up' in self.keys_pressed:
                self.spaceship.thrust()

        self.spaceship.move()
        for asteroid in self.asteroids:
            asteroid.move()
        for bullet in self.bullets[:]:
            bullet.move()
            bullet.lifetime -= dt
            if bullet.lifetime <= 0:
                self.remove_widget(bullet)
                self.bullets.remove(bullet)

        for asteroid in self.asteroids[:]:
            if self.spaceship.collide_widget(asteroid):
                self.lives -= 1
                self.remove_widget(asteroid)
                self.asteroids.remove(asteroid)
                if self.lives > 0:
                    self.remove_widget(self.spaceship)
                    self.spaceship = Spaceship()
                    self.spaceship.center = self.center
                    self.add_widget(self.spaceship)
                else:
                    self.game_state = 'game_over'
                    self.game_over_label.opacity = 1
            for bullet in self.bullets[:]:
                if bullet.collide_widget(asteroid):
                    self.score += 100 * (4 - asteroid.size_level)
                    asteroid.split(self)
                    self.remove_widget(asteroid)
                    self.remove_widget(bullet)
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    break

        if randint(1, 100) < 2 and len(self.asteroids) < 5:
            self.spawn_asteroid()

        self.score_label.text = f'Score: {self.score}'
        self.lives_label.text = f'Lives: {self.lives}'

class AsteroidsApp(App):
    def build(self):
        return GeneratedGameWidget()

if __name__ == '__main__':
    AsteroidsApp().run()
"""

        # Initialize TextInput for displaying generated code
        self.code_display = TextInput(
            text=asteroids_code,
            hint_text='Generated code will appear here',
            multiline=True,
            readonly=False,
            size_hint=(1, 0.3)
        )
        self.layout.add_widget(self.code_display)

        # Create button to run the generated game
        run_btn = Button(text='Run Game', size_hint=(1, 0.1))
        # Bind button press to run_game method
        run_btn.bind(on_press=self.run_game)
        self.layout.add_widget(run_btn)

        # Return the main layout
        return self.layout

    # Handle the generation of game code
    def generate_code(self, instance):
        # Get and validate API key
        api_key = self.api_key_input.text.strip()
        if not api_key:
            self.code_display.text = 'Error: Please provide an API key'
            return

        # Get and validate game prompt
        prompt = self.prompt_input.text.strip()
        if not prompt:
            self.code_display.text = 'Error: Please enter a prompt'
            return

        # Get prefix and suffix for the prompt
        prefix = self.prefix_input.text.strip()
        suffix = self.suffix_input.text.strip()
        # Combine prompt components
        full_prompt = f"{prefix} {prompt} {suffix}".strip()

        # Call the Grok API with the full prompt
        self.call_grok_api(full_prompt, api_key)

    # Make API call to Grok for code generation
    def call_grok_api(self, full_prompt, api_key):
        # Define API endpoint
        api_url = 'https://api.x.ai/v1/chat/completions'
        # Set headers with API key and content type
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        # Prepare request data
        data = json.dumps({
            'model': 'grok-3',  # Specify the model, e.g., 'grok-3'
            'messages': [
                {'role': 'user', 'content': full_prompt}
            ],
            'max_tokens': 16000,  # Optional: adjust as needed
            'temperature': 0.7  # Optional: adjust as needed
        })

        # Handle successful API response
        def on_success(req, result):
            try:
                # Extract generated code from response
                content = result['choices'][0]['message']['content']
                self.code_display.text = content
            except (KeyError, IndexError, TypeError):
                # Handle parsing errors
                self.code_display.text = 'Error: Unable to parse API response'

        # Handle failed API request
        def on_failure(req, result):
            self.code_display.text = 'Error: API request failed\n\nreq: {req}\n\nresult: {result}'

        # Handle network or other errors
        def on_error(req, error):
            self.code_display.text = f'Error: {str(error)}'

        # Send POST request to Grok API
        UrlRequest(
            api_url,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error,
            req_body=data,
            req_headers=headers,
            method='POST'
        )

    # Execute the generated game code
    def run_game(self, instance):
        # Get the generated code
        generated_code = self.code_display.text
        # Check if code is present
        if not generated_code:
            self.code_display.text = 'Error: No valid code to run'
            return
        try:
            # Create a namespace for code execution
            namespace = {}
            # Execute the generated code
            exec(generated_code, namespace)
            # Check if GeneratedGameWidget is defined
            if 'GeneratedGameWidget' in namespace:
                # Instantiate and display the game widget
                game_widget = namespace['GeneratedGameWidget']()
                self.layout.clear_widgets()
                self.layout.add_widget(game_widget)
            else:
                self.code_display.text = 'Error: Generated code does not define GeneratedGameWidget'
        except Exception as e:
            # Handle execution errors
            self.code_display.text = f'Error running code: {str(e)}'

# Run the application if executed directly
if __name__ == '__main__':
    GameGeneratorApp().run()