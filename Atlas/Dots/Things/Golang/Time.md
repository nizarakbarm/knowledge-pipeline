---
top:
  - "[[Golang]]"
in:
  - "[[Concepts]]"
  - "[[Things]]"
related:
created: 2025-10-15
---

#### Intro
- a **type** describing a moment in time
- can be accessed, compared, and manipulated thorugh its methods
- can use `time` package
- current date and time: `time.Now` function
- `time.Parse` function : parses strings into values of type `Time`
- has a special way of how you define the layout for parsing -> write an example of layout using the values from this special timestamp -> `Mon Jan 2 15:04:05 -0700 MST 2006`
- example:
```Golang
import "time" 

func parseTime() time.Time { 
	date := "Tue, 09/22/1995, 13:00" 
	layout := "Mon, 01/02/2006, 15:04" 

	t, err := time.Parse(layout,date) // time.Time, error 
} 

// => 1995-09-22 13:00:00 +0000 UTC
```
- `Time.Format()` returns a string representation of time
```Golang
import (
	"fmt"
	"time"
)

func main() {
	t := time.Date(1995, time.September, 22, 13, 0, 0, 0, time.UTC)
	formattedTime := t.Format("Mon, 01/02/2006, 15:04") // string
	fmt.Println(formattedTime)
}

// => Fri, 09/22/1996, 13:00
```


#### Layout Options
For custom layout, there is available predefined date and timestamp format constants:


| Time        | Options                                    |
| ----------- | ------------------------------------------ |
| Year        | 2006; 06                                   |
| Month       | Jan; January; 01; 1                        |
| Day         | 02; 2; `_2` (For preceding 0)              |
| Weekday     | Mon; Monday                                |
| Hour        | 15 (24 hour time format); 3; 03 (AM or PM) |
| Minute      | 04; 4                                      |
| Second      | 05; 5                                      |
| AM/PM Mark  | PM                                         |
| Day of Year | 002; `_ _ 2`                               |

See [time package - time - Go Packages](https://golang.org/pkg/time/#Time) for more information about various methods for accessing a particular time
Also has another type, `Duration`, representing elapsed time, plus support for locations/time zones, timers, and other related functionality