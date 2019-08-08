package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"regexp"
	"time"
)

func toMap(src interface{}, panicWhenError bool) (dst map[string]interface{}, ok bool) {
	if dst, ok = src.(map[string]interface{}); panicWhenError && !ok {
		panic("类型断言,失败")
	}
	return
}

func toSlc(src interface{}, panicWhenError bool) (dst []interface{}, ok bool) {
	if dst, ok = src.([]interface{}); panicWhenError && !ok {
		panic("类型断言,失败")
	}
	return
}

//MyExpect omit.
type MyExpect struct {
	stdinReader *bufio.Reader
}

func newMyExpect() *MyExpect {
	curData := new(MyExpect)
	curData.stdinReader = bufio.NewReader(os.Stdin)
	return curData
}

func (thls *MyExpect) run(filename string) {
	arrCmdLine, _ := thls.loadFile(filename, true)
	thls.doArray(arrCmdLine, false, nil)
}

func (thls *MyExpect) loadFile(filename string, panicWhenError bool) (slc []interface{}, err error) {
	var byteSlice []byte
	if byteSlice, err = ioutil.ReadFile(filename); err != nil {
		if panicWhenError {
			panic(err)
		} else {
			return
		}
	}
	if err = json.Unmarshal(byteSlice, &slc); err != nil {
		if panicWhenError {
			panic(err)
		} else {
			return
		}
	}
	return
}

func (thls *MyExpect) doArray(arrCmdLine []interface{}, byExpect bool, expContinue *bool) {
	if expContinue != nil {
		*expContinue = false
	}
	for _, tmpCmdData := range arrCmdLine {
		curCmdLine, isOk := toMap(tmpCmdData, true)
		if false {
		} else if tmpCmdData, isOk = curCmdLine["expect"]; isOk {
			thls.doExpect(tmpCmdData)
		} else if tmpCmdData, isOk = curCmdLine["sleep"]; isOk {
			thls.doSleep(tmpCmdData)
		} else if tmpCmdData, isOk = curCmdLine["send"]; isOk {
			thls.doSend(tmpCmdData)
		} else if tmpCmdData, isOk = curCmdLine["exp_continue"]; isOk {
			thls.doExpContinue(tmpCmdData, byExpect, expContinue)
			break
		} else {
			panic(curCmdLine)
		}
	}
}

func (thls *MyExpect) doExpect(curAction interface{}) {
	allAction, _ := toMap(curAction, true)
	keyDefault := "" //如果所有的key都找不到,就找它.
	valDefault, _ := allAction[keyDefault]

	var err error
	var line string
	var matched bool
	var existExpContinue bool
	for !matched {
		if line, err = thls.stdinReader.ReadString('\n'); err != nil {
			panic(err)
		}
		for key, val := range allAction {
			if key == keyDefault {
				continue
			}
			if matched, err = regexp.MatchString(key, line); err != nil {
				panic(err)
			}
			if matched {
				thls.doArray(val.([]interface{}), true, &existExpContinue)
				break
			}
		}
		if !matched && valDefault != nil {
			thls.doArray(valDefault.([]interface{}), true, &existExpContinue)
		}
		if existExpContinue {
			matched = false
		}
	}
}

func (thls *MyExpect) doSend(curAction interface{}) {
	//如果我用键盘敲击了4次按键，分别是【x、y、z、回车键】，那么实际上往cin里面写进去了5个字符，分别是【120、121、122、13、10】.
	//【13=>'\r'】;【10=>'\n'】;
	tmpAction := curAction.(string)
	if false {
		fmt.Fprintf(os.Stdout, "%s\n", tmpAction)
	} else {
		fmt.Fprintf(os.Stdout, "%s", tmpAction)
	}
}

func (thls *MyExpect) doSleep(curAction interface{}) {
	tmpAction := curAction.(float64)
	time.Sleep(time.Duration(tmpAction*1000*1000) * time.Microsecond)
}

func (thls *MyExpect) doExpContinue(curAction interface{}, byExpect bool, expContinue *bool) {
	if !byExpect {
		panic(byExpect)
	}
	*expContinue = true
}

func main() {
	var argHelp bool
	var argJSON string
	flag.BoolVar(&argHelp, "help", false, "display this help and exit.")
	flag.StringVar(&argJSON, "json", "json.json", "json configuration file.")
	flag.Parse()
	if argHelp {
		flag.Usage()
		exampleJSON()
		return
	}
	myexpect := newMyExpect()
	myexpect.run(argJSON)
}

func exampleJSON() {
	content := `
example_json_content:
[
    { "send": "please input password: " },
    { "expect": { "pwd": [ { "send": "Password right\r\n" } ],
                     "": [ { "send": "Password wrong, please try again.\r\nplease input password: " },
                           { "exp_continue": "" },
                           { "send": "test\r\n" }
                         ]
                }
    },
    { "send": "sleep_begin\r\n" },
    { "sleep": 1.5 },
    { "send": "sleep_end\r\n" },
    { "send": "will_exit\r\n" }
]
`
	fmt.Println(content)
}
