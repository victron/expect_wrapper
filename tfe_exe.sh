#!/usr/bin/expect
set timeout 120
set send_slow {10 .001}
set prompt "tfe>> "

set log_file_name "./logs/vmdata_[exec date +%Y-%m-%d_%H-%M].log"
log_file $log_file_name

# Get the commands to run, one per line
set f [open "commands.txt"]
set commands [split [read $f] "\n"]
close $f


send_user "\n############\n"
send_user "scripting tfe"
send_user "\n############\n"
spawn tfe


expect {
  timeout { send_user "\n====> ERROR: waiting to long to connect... \n"; exit 1 }
  eof { send_user "\n====> ERROR: EOF \n"; exit 1 }
  "*....cannot connect" { 
      send_user "\n====> ERROR: cannot connect to some tenvProc; exiting in 10 sec....\n"
      sleep 10
      send -- "exit\r"
      exit 1
      }
  $prompt {
      send_user "\n====> INFO: connected....\n"
      send -- "\r"
      }
}

foreach cmd $commands {
    expect {
        timeout { 
            send_user "\n====> waiting to long to execute...\n"
            send_user "\n====> ERROR: cannot connect to some tenvProc; exiting in 10 sec....\n"
            sleep 10
            send -- "exit\r"
            exit 1
            }
        
        $prompt {
            send_user "\n====> INFO: sending command from file...\n"
            send -- "$cmd\r"
            }
    }
}

send "exit\r"
close