function start_run () {
    basic.showString("-")
    datalogger.deleteLog(datalogger.DeleteType.Full)
    datalogger.setColumnTitles(
    "Time",
    "Dust",
    "Temprature",
    "Light",
    "Fire",
    "Error",
    "Front Sonar:bit",
    "Motor Sonar:bit",
    "Motion_detected",
    "Light-detected"
    )
    run = true
    while (true) {
        basic.showNumber(object_count)
        Send_data("motor.run")
        while (true) {
            if (!(Environment.PIR(DigitalPin.P15))) {
                distance = Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P13)
                if (distance < 300 && distance != 0 || object_detected()) {
                    break;
                }
            }
        }
        if (object_detected()) {
            basic.showLeds(`
                . # # # .
                # # # # #
                # # # # #
                # # # # #
                . # # # .
                `)
            object_count += 1
            if (object_count == object_count_limit) {
                turnBack()
                basic.pause(5000)
                turnRight()
            } else {
                while (true) {
                    if (!(object_detected())) {
                        break;
                    }
                }
                Send_data("motor.stop")
            }
        } else {
            Send_data("motor.stop")
            basic.showLeds(`
                # # # # #
                . . . . .
                . . . . .
                . . # . .
                . . # . .
                `)
            Ultrasonicset_servo_position()
            Send_data("motor.run")
            while (true) {
                if (Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P13) > 500) {
                    break;
                }
            }
            Send_data("motor.stop")
            Send_data("servo.centre")
        }
    }
}
function change_limit (num: number) {
    if (run) {
        control.reset()
    } else {
        if (num == -1) {
            if (object_count_limit != 1) {
                object_count_limit += num
            }
        } else {
            if (object_count_limit != 0) {
                object_count_limit += num
            }
        }
        basic.showNumber(object_count_limit)
    }
}
function Send_data (data: string) {
    Message_arrived = false
    radio.sendString(data)
    while (true) {
        if (Message_arrived) {
            break;
        } else {
            basic.pause(100)
            radio.sendString(data)
        }
    }
}
datalogger.onLogFull(function () {
    music.play(music.tonePlayable(988, music.beat(BeatFraction.Breve)), music.PlaybackMode.UntilDone)
    basic.showLeds(`
        # # # # #
        . # # # .
        . . # . .
        . . . . .
        . . # . .
        `)
    datalogger.deleteLog(datalogger.DeleteType.Fast)
})
function getCompassEnd (currentPosition: number) {
    endPositionsList = []
    for (let index = 0; index <= 9; index++) {
        endPosition = currentPosition + (20 + index)
        if (endPosition > 359) {
            endPosition = endPosition - 359
        }
        endPositionsList.push(endPosition)
    }
    return endPositionsList
}
function Ultrasonicset_servo_position () {
    Send_data("ultramotor.left")
    basic.pause(1000)
    distance = Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P14)
    Send_data("ultramotor.right")
    basic.pause(1000)
    if (distance >= Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P14)) {
        Send_data("servo.left")
    } else {
        Send_data("servo.right")
    }
}
function turnBack () {
    Send_data("motor.reverse")
    while (true) {
        if (object_detected()) {
            break;
        }
    }
    while (true) {
        if (!(object_detected())) {
            break;
        }
    }
}
input.onButtonPressed(Button.A, function () {
    change_limit(-1)
})
function object_detected () {
    return Environment.ReadLightIntensity(AnalogPin.P2) < 5
}
function turnRight () {
    Send_data("motor.stop")
    startCompassPosition = input.compassHeading()
    Send_data("servo.right")
    Send_data("motor.run")
    while (getCompassEnd(startCompassPosition).indexOf(input.compassHeading()) != -1) {
        basic.pause(1)
    }
    Send_data("motor.stop")
    Send_data("servo.centre")
}
input.onButtonPressed(Button.AB, function () {
    start_run()
})
radio.onReceivedString(function (receivedString) {
    if (receivedString == "MessageGet") {
        Message_arrived = true
    }
})
input.onButtonPressed(Button.B, function () {
    change_limit(1)
})
input.onLogoEvent(TouchButtonEvent.Pressed, function () {
    input.calibrateCompass()
})
function check_for_errors () {
    if (Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P13) == 0 || Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P14) == 0) {
        music.play(music.tonePlayable(262, music.beat(BeatFraction.Whole)), music.PlaybackMode.InBackground)
        errors = true
    } else {
        errors = false
    }
}
function Log_data (log: boolean) {
    OLED.clear()
    OLED.writeStringNewLine("Dust: " + Environment.ReadDust(DigitalPin.P9, AnalogPin.P1))
    OLED.writeStringNewLine("Compass: " + input.compassHeading() + "`")
    OLED.writeStringNewLine("Front Sonar: " + Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P13) + " mm")
    OLED.writeStringNewLine("Motor Sonar: " + Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P14) + " mm")
    OLED.writeStringNewLine("Motion: " + Environment.PIR(DigitalPin.P15))
    OLED.writeStringNewLine("Detection light: " + Environment.ReadLightIntensity(AnalogPin.P2) + "%")
    OLED.writeStringNewLine("Run: " + run)
    OLED.writeStringNewLine("Error: " + errors)
    if (log) {
        datalogger.log(
        datalogger.createCV("Time", input.runningTime()),
        datalogger.createCV("Dust", Environment.ReadDust(DigitalPin.P9, AnalogPin.P1)),
        datalogger.createCV("Temprature", input.temperature()),
        datalogger.createCV("Light", input.lightLevel()),
        datalogger.createCV("Compass", input.compassHeading()),
        datalogger.createCV("Error", errors),
        datalogger.createCV("Front Sonar:bit", Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P13)),
        datalogger.createCV("Motor Sonar:bit", Environment.sonarbit_distance(Environment.Distance_Unit.Distance_Unit_mm, DigitalPin.P14)),
        datalogger.createCV("Motion_detected", Environment.PIR(DigitalPin.P15)),
        datalogger.createCV("Light-detected", Environment.ReadLightIntensity(AnalogPin.P2))
        )
    }
}
let errors = false
let startCompassPosition = 0
let endPosition = 0
let endPositionsList: number[] = []
let Message_arrived = false
let distance = 0
let object_count = 0
let run = false
let object_count_limit = 0
basic.pause(input.compassHeading())
object_count_limit = 3
OLED.init(128, 64)
OLED.writeStringNewLine("Waiting to start")
basic.showLeds(`
    . . # . .
    . # . # .
    . # . # .
    . # . # .
    # . . . #
    `)
Send_data("servo.centre")
basic.showNumber(object_count_limit)
loops.everyInterval(2000, function () {
    if (run) {
        if (Environment.PIR(DigitalPin.P15)) {
            radio.sendNumber(1)
        } else {
            radio.sendNumber(0)
        }
        Log_data(true)
        check_for_errors()
    } else {
        Log_data(false)
    }
})
