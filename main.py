def fire():
    return pins.digital_read_pin(DigitalPin.P16) == 0
def Send_data(data: str):
    global Message_arrived
    if connect:
        Message_arrived = False
        radio.send_string(data)
        while connect:
            basic.pause(200)
            if Message_arrived:
                break
            else:
                radio.send_string(data)

def on_log_full():
    music.play(music.tone_playable(988, music.beat(BeatFraction.BREVE)),
        music.PlaybackMode.UNTIL_DONE)
    basic.show_leds("""
        # # # # #
        . # # # .
        . . # . .
        . . . . .
        . . # . .
        """)
    datalogger.delete_log(datalogger.DeleteType.FAST)
datalogger.on_log_full(on_log_full)

def on_logo_long_pressed():
    swith_mode()
input.on_logo_event(TouchButtonEvent.LONG_PRESSED, on_logo_long_pressed)

def Ultrasonicset_servo_position():
    global distance_left, distance_right
    Send_data("ultramotor.left")
    basic.pause(2000)
    distance_left = Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P14)
    Send_data("ultramotor.right")
    basic.pause(2000)
    distance_right = Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P14)
    if distance_left > distance_right:
        basic.show_arrow(ArrowNames.SOUTH_WEST)
        Send_data("servo.left")
    else:
        basic.show_arrow(ArrowNames.SOUTH_EAST)
        Send_data("servo.right")

def on_button_pressed_a():
    global Line_mode
    music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
        music.PlaybackMode.IN_BACKGROUND)
    Line_mode = True
    basic.show_string("L")
input.on_button_pressed(Button.A, on_button_pressed_a)

def swith_mode():
    global connect
    music.play(music.tone_playable(988, music.beat(BeatFraction.WHOLE)),
        music.PlaybackMode.IN_BACKGROUND)
    connect = not (connect)
    if connect:
        basic.show_leds("""
            . . # # .
            # . # . #
            . # # # .
            # . # . #
            . . # # .
            """)
    else:
        basic.show_icon(IconNames.NO)
    basic.clear_screen()
def object_detected():
    return Environment.read_light_intensity(AnalogPin.P2) < 50

def on_button_pressed_ab():
    global Line_mode
    music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
        music.PlaybackMode.IN_BACKGROUND)
    Line_mode = not (Line_mode)
    basic.show_string("N")
input.on_button_pressed(Button.AB, on_button_pressed_ab)

def on_received_string(receivedString):
    global Message_arrived, Line, Receveicedmessage
    if receivedString == "MessageGet":
        Message_arrived = True
    else:
        Line = "" + receivedString.char_at(0) + receivedString.char_at(1)
        Receveicedmessage = ""
        index = 0
        while index <= len(receivedString) - 3:
            Receveicedmessage = "" + Receveicedmessage + receivedString.char_at(index + 2)
            index += 1
        radio.send_string("MessageGet")
radio.on_received_string(on_received_string)

def on_button_pressed_b():
    global Line_mode
    music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
        music.PlaybackMode.IN_BACKGROUND)
    Line_mode = False
    basic.show_string("R")
input.on_button_pressed(Button.B, on_button_pressed_b)

def on_logo_pressed():
    swith_mode()
input.on_logo_event(TouchButtonEvent.PRESSED, on_logo_pressed)

def Log_data():
    datalogger.log(datalogger.create_cv("Time", input.running_time()),
        datalogger.create_cv("Dust", Environment.read_dust(DigitalPin.P9, AnalogPin.P1)),
        datalogger.create_cv("Temprature", input.temperature()),
        datalogger.create_cv("Light", input.light_level()),
        datalogger.create_cv("Fire", fire()),
        datalogger.create_cv("Noise", input.sound_level()),
        datalogger.create_cv("Sonar:bits",
            "" + str(Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P13)) + "*" + ("" + str(Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P14)))),
        datalogger.create_cv("Motion_detected", Environment.PIR(DigitalPin.P15)),
        datalogger.create_cv("Light-detected",
            Environment.read_light_intensity(AnalogPin.P2)),
        datalogger.create_cv("Lines", Line))
    try:
        OLED.clear()
        OLED.write_string_new_line("Dust: " + ("" + str(Environment.read_dust(DigitalPin.P9, AnalogPin.P1))))
        OLED.write_string_new_line("Fire: " + ("" + str(fire())))
        OLED.write_string_new_line("Noise: " + ("" + str(input.sound_level())))
        OLED.write_string_new_line("Sonar 1: " + ("" + str(Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P13))))
        OLED.write_string_new_line("Sonar 2: " + ("" + str(Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P14))))
        OLED.write_string_new_line("Motion: " + ("" + str(Environment.PIR(DigitalPin.P15))))
        OLED.write_string_new_line("Light detection: " + ("" + str(Environment.PIR(DigitalPin.P15))))
        OLED.write_string_new_line("Lines: " + Line)

def Line_navigation():
    if Line == "11" or Line == "00":
        Send_data("servo.centre")
    elif Line == "01":
        Send_data("servo.right")
    else:
        Send_data("servo.left")
alarm = False
Receveicedmessage = ""
Message_arrived = False
distance_right = 0
distance_left = 0
Line = ""
Line_mode = False
connect = False
basic.show_leds("""
    . . . . .
    . . . . .
    # . # . #
    . . . . .
    . . . . .
    """)
datalogger.delete_log(datalogger.DeleteType.FULL)
datalogger.mirror_to_serial(True)
datalogger.set_column_titles("Time",
    "Dust",
    "Temprature",
    "Light",
    "Fire",
    "Noise",
    "Sonar:bits",
    "Motion_detected",
    "Light-detected",
    "Lines")
connect = False
Line_mode = True
Line = "--"
Line_mode = False
distance_left = 0
distance_right = 0
Message_arrived = False
Receveicedmessage = ""
basic.show_string("-")

def on_forever():
    global alarm
    for index2 in range(100):
        if fire() or input.sound_level() >= 170:
            alarm = True
            for index22 in range(5):
                music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
                    music.PlaybackMode.UNTIL_DONE)
                basic.pause(input.sound_level())
            alarm = False
        elif Environment.PIR(DigitalPin.P15):
            alarm = True
            music.play(music.tone_playable(131, music.beat(BeatFraction.BREVE)),
                music.PlaybackMode.UNTIL_DONE)
            basic.pause(input.sound_level())
            music.play(music.tone_playable(131, music.beat(BeatFraction.BREVE)),
                music.PlaybackMode.UNTIL_DONE)
            alarm = False
        basic.pause(50)
    Log_data()
basic.forever(on_forever)

def on_forever2():
    if connect:
        if not (alarm):
            if Line_mode:
                Send_data("motor.run")
                while not (object_detected()):
                    Line_navigation()
                Ultrasonicset_servo_position()
                Send_data("motor.run")
                while Line != "01" and Line != "10":
                    basic.pause(1)
                Line_navigation()
            else:
                basic.show_arrow(ArrowNames.NORTH)
                Send_data("servo.centre")
                Send_data("motor.run")
                while Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P13) > 300 and not (object_detected()):
                    basic.pause(1)
                Send_data("motor.stop")
                if object_detected():
                    music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
                        music.PlaybackMode.UNTIL_DONE)
                    music.play(music.tone_playable(494, music.beat(BeatFraction.WHOLE)),
                        music.PlaybackMode.UNTIL_DONE)
                    music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
                        music.PlaybackMode.UNTIL_DONE)
                else:
                    Ultrasonicset_servo_position()
                    Send_data("motor.run")
                    while True:
                        if Environment.sonarbit_distance(Environment.Distance_Unit.DISTANCE_UNIT_MM, DigitalPin.P13) > 300:
                            break
                    Send_data("servo.centre")
        else:
            basic.show_leds("""
                . . # . .
                . . # . .
                . . # . .
                . . . . .
                . . # . .
                """)
basic.forever(on_forever2)
