use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;
use std::collections::HashMap;

fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn time_to_minutes_passed(t: &str) -> i32 {
    let mut t_split = t.split(":");
    let hours: i32 = t_split.next().unwrap().parse().unwrap();
    let minutes: i32 = t_split.next().unwrap().parse().unwrap();

    hours * 60 + minutes
}


fn main() {
    let mut tagMap = HashMap::new();
    let mut lastTime = 0;
    let mut tags = Vec::new();

    /*
     * Todo List 
     * -----
     * 1. Find time between blocks
     * 2. For all time blocks, add that time to proper tags
     * TODO: Eventually use dates to make pretty graph or something
     */


    if let Ok(lines) = read_lines("./daily") {
        for line in lines {
            let line = line
                .unwrap();

            let vec = line
                .split(" ")
                .collect::<Vec<_>>();

            // Don't process FIN or Dates, reset variables on dates
            if vec.len() == 1 {
                lastTime = 0;
                tags.clear();
                continue;
            }

            let x:char = vec[0]
                .chars()
                .nth(0)
                .unwrap();

            // Set this to last time + add tags
            match x {
                '0'..='9' => {
                    let curTime = time_to_minutes_passed(vec[0]);
                    if curTime != 0 {
                        for tag in tags.iter_mut() {
                            let tagTime = tagMap.entry(&tag).or_insert(0);
                            *tagTime += curTime - lastTime;
                        }
                    }
                    tags.clear();
                    if vec[1] == "FIN" { continue }
                    for x in vec.iter() {
                        let mut chars = x.chars();
                        if chars.nth(0).unwrap() == '@' {
                            chars.next();
                            tags.push(chars.as_str());
                        }
                    }
                    lastTime = time_to_minutes_passed(vec[0]);
                }
                _ => continue,
            }
        }
    }
}
