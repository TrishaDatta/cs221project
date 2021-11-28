package main

import (

    "net/http"
    "fmt"
    "os"
    "strings"
    "github.com/corpix/uarand"
    "github.com/PuerkitoBio/goquery"
    "github.com/advancedlogic/GoOse"
    "bufio"
    "sync"
    "time"
    "net/url"
    "context"
    "encoding/json"
    "io/ioutil"
    "bytes"

)

type Sites struct {
    url    string
}

type CallResponse struct {
    val  bool
}
var num_scraped int 
var new_urls []string 
var crawled_urls [] string

//var NUM_PROCESSES int 




func contains(s []string, e string) bool {
    for _, a := range s {
        if a == e {
            return true
        }
    }
    return false
}

func crawlHelper(ctx context.Context,wg *sync.WaitGroup,Site *Sites,linkFile *os.File,imageFile *os.File, failed *os.File, linkNum int ,html_files *os.File ) {
    //defer wg.Done() // decrements the WaitGroup counter by one when the function returns
    defer wg.Done()
    //d := time.Now().Add(15*time.Second)
    ctx, cancel := context.WithTimeout(ctx, 60*time.Second)
    //defer cancel()
    for {
        select {
        case <-ctx.Done(): // Done returns a channel that's closed when work done on behalf of this context is canceled
            num_scraped +=1
            //wg.Done()
            cancel()
            //fmt.Println("Exiting from writing go routine")
            return
        case <-CrawlGoRoutine(ctx,Site,linkFile,imageFile,failed,linkNum,html_files): // pushes a boolean into the 
            num_scraped +=1
            //wg.Done()
            cancel()
            return 
        }
    }
}

func CrawlGoRoutine(ctx context.Context, Site *Sites,linkFile *os.File,imageFile *os.File, failed *os.File, linkNum int ,html_files *os.File) <-chan *CallResponse {  

    defer func() {
        if err := recover(); err != nil {
            fmt.Println("panic occurred:", err)
        }
    }()

    respChan := make(chan *CallResponse, 1)
    website := strings.Split(Site.url, "//")
    if len(website ) < 2 {
        respChan <- &CallResponse{false}
        return respChan  
        
    }
    if len(website[1]) == 0 {
        respChan <- &CallResponse{false}
        return respChan 
    }

    domain := strings.Split(website[1], "/")

    base_url := website[0] +"//"+ domain[0]
    client := &http.Client{Timeout: 20 * time.Second,}



    var (
        err  error 
        response *http.Response
        retries int =2
        
    )

    for retries > 0 {
        req, err := http.NewRequest("GET", Site.url, nil)
        if err != nil {
            retries =-1
            continue 
        } 
        //req.Header.Set("User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0")
        req.Header.Set("User-Agent",uarand.GetRandom())
        response, err = client.Do(req)
        if err != nil {
            retries =-1
            //os.Exit(3)
        } else {
            break
        }
    }
    if response == nil {
        respChan <- &CallResponse{false}
        return respChan
    }
    body, err := ioutil.ReadAll(response.Body)
    current_file := html_files
    g := goose.New()
    article, err := g.ExtractFromURL(Site.url)
    if err != nil {
        var m map[string]string
        m = make(map[string]string)
        //var buf bytes.Buffer
        //tee := io.TeeReader(response.Body, &buf)
        //fmt.Println(&buf)
        blah := string(body)
        m["rawhtml"] = blah
        m["url"] = Site.url
        article_data, err := json.MarshalIndent(m, "", " ")
        if err != nil {
			fmt.Println("ERROR: " + err.Error())
        } 

        if _, err := current_file.Write([]byte(article_data)); err != nil {       
            fmt.Println("ERROR: " + err.Error())
        }  

        fmt.Println("Natural Finished getting article.")

    }  else {
        article_data, err := json.MarshalIndent(article, "", " ")
        if err != nil {
			fmt.Println("ERROR: " + err.Error())
            respChan <- &CallResponse{false}
            return respChan 
        } 

        if _, err := current_file.Write([]byte(article_data)); err != nil {
			fmt.Println("ERROR: " + err.Error())
            respChan <- &CallResponse{false}
            return respChan 
        }  
        fmt.Println("Finished getting article.")
    }
     
    if err != nil {
        respChan <- &CallResponse{false}
        return respChan 
    } 
    retries = 2
    if response == nil {
        respChan <- &CallResponse{false}
        return respChan 
    }

    r := bytes.NewReader(body)
    document, err := goquery.NewDocumentFromReader(r)
    // Create a goquery document from the HTTP response
    if err != nil {
            for retries > 0 {
            document, err = goquery.NewDocumentFromReader(r)
            if err != nil {
                retries=-1 
            } else {
                break
            }
        }
    }  else {
        if err != nil {
            _, err = failed.WriteString(Site.url + "\n")
            if err != nil {
                fmt.Println("ERROR: " + err.Error())
                respChan <- &CallResponse{false}
                return respChan 
            }
            respChan <- &CallResponse{false}
            return respChan
        }
    }
    
    if err != nil {
        _, err = failed.WriteString(Site.url + "\n")
        if err != nil {
            fmt.Println("ERROR: " + err.Error())
            respChan <- &CallResponse{false}
            return respChan
        }

        respChan <- &CallResponse{false}
        return respChan
    }




    // Find all links and process them with the function
    // defined earlier
   // document.Find("a").Each(processElement)    
   if document != nil {
        document.Find("a").Each(func(index int, item *goquery.Selection) {
            // See if the href attribute exists on the element
            href, exists := item.Attr("href")
            if exists {
                if href!= "" {
                    first1 :=  href[0]
                    if strings.Contains(string(first1),"/") {
                        before := strings.Split(href, "#")
                        if !contains(crawled_urls,base_url+before[0]) {
                            new_urls = append(new_urls, base_url+before[0])
                            crawled_urls = append(crawled_urls, base_url+before[0])
                        }
                        _, err := linkFile.WriteString(Site.url +" , " +base_url+href+"\n")
                        if err != nil {
                            fmt.Println("ERROR: " + err.Error())
                            return 
                        }
                       
                    } else {
                        website1 := strings.Split(href, "//")
                        if len(website1 ) < 2 {
                            return 
                        }
                        if len(website1[1]) == 0 {
                            return 
                        }						

                        //domain1 := strings.Split(website1[1], "/")
                        //domain2 := strings.Replace(domain1[0], "www.", "", -1)
                        before := strings.Split(href, "#")
                        //new_urls = append(new_urls, href)
                        if !contains(crawled_urls,before[0]) {
                            new_urls = append(new_urls, before[0])
                            crawled_urls = append(crawled_urls, before[0])                        
                            
                        }
                        _, err = linkFile.WriteString(Site.url +" , " +href+"\n")
                            if err != nil {
                                fmt.Println("ERROR: " + err.Error())
                                return 
                            }
                    }

                } 
                
            }
        })
        
        
        // use CSS selector found with the browser inspector
        // for each, use index and item
        document.Find("*").Each(func(index int, item *goquery.Selection) {
            linkTag := item.Find("img")
            link, _ := linkTag.Attr("src")
            if link != "" {
                first1 :=  link[0]
                if strings.Contains(string(first1),"/") {
                    _, err := imageFile.WriteString(Site.url +" , " +base_url+link+"\n")
                    if err != nil {
                        fmt.Println("ERROR: " + err.Error())
                        return 
                    }
                } else {
                     _, err := imageFile.WriteString(Site.url +" , " +link+"\n")
                     if err != nil {
                        fmt.Println("ERROR: " + err.Error())
                        return 
                    }
                }
            }
        })
   } else {
        _, err = failed.WriteString(Site.url + "\n")
        if err != nil {
            fmt.Println("ERROR: " + err.Error())
            respChan <- &CallResponse{false}
            return respChan
        }
        respChan <- &CallResponse{false}
        return respChan 
   }
   //num_scraped +=1
   fmt.Println(Site.url)
   respChan <- &CallResponse{true}
   return respChan

}






func unique(stringSlice []string) []string {
    keys := make(map[string]bool)
    list := []string{} 
    for _, entry := range stringSlice {
        if _, value := keys[entry]; !value {
            keys[entry] = true
            list = append(list, entry)
        }
    }    
    return list
}

func main() {
    f, err := os.Open("missing")
    if err != nil {
        fmt.Println("ERROR: " + err.Error())
        return
    }
    num_scraped := 0 
    var urls []string
    scanner := bufio.NewScanner(f)
    for scanner.Scan() {
        urlt  := scanner.Text()
        t := strings.TrimSpace(urlt)
        t = strings.ToLower(t)
        urls = append(urls,t)
    }
    all_urls := unique(urls)
	fmt.Println(len(all_urls))
   
    new_urls= []string{}
    crawled_urls = []string{}

    links, err := os.OpenFile("LINK_FILE.txt",os.O_CREATE|os.O_WRONLY, os.ModeAppend)
    if err != nil {
        fmt.Println("ERROR: " + err.Error())
        return
    }

    failed, err := os.OpenFile("FAILED_FILE.txt",os.O_CREATE|os.O_WRONLY, os.ModeAppend)
    if err != nil {
        fmt.Println("ERROR: " + err.Error())
        return
    }

    image, err := os.OpenFile("IMAGE_FILE.txt",os.O_CREATE|os.O_WRONLY, os.ModeAppend)
    if err != nil {
        fmt.Println("ERROR: " + err.Error())
        return
    }

    //var html_files = make(map[string]*os.File)

    nlonger, err := os.OpenFile("FILES_TO_KEEP_TRACK_OF_WHAT_IS_SCRAPED_FOLLOWING_PROCESS_KILLS.txt",os.O_CREATE|os.O_WRONLY, os.ModeAppend)
    if err != nil {
        fmt.Println("ERROR: " + err.Error())
        return
    }
    scraped, err := os.OpenFile("FILES_TO_KEEP_TRACK_OF_WHAT_IS_SCRAPED_FOLLOWING_PROCESS_KILLS_2.txt",os.O_CREATE|os.O_WRONLY, os.ModeAppend)
    if err != nil {
        fmt.Println("ERROR: " + err.Error())
        return
    }
    NUM_PROCESSES := 50
    // Dummy channel to coordinate the number of concurrent goroutines.
    // This channel should be buffered otherwise we will be immediately blocked
    // when trying to fill it.
    //concurrentGoroutines := make(chan struct{}, NUM_PROCESSES)
    sem := make(chan int, NUM_PROCESSES)

    var wg sync.WaitGroup

    file, err := os.OpenFile("HTML_FILE_NAME .txt",os.O_CREATE|os.O_WRONLY, os.ModeAppend)
    if err != nil {
        fmt.Println("ERROR: " + err.Error())
        return
    }
    html_files := file
    NUM_HOPS := 1
    /*unique_urls := []string{}
    for _, url_d := range all_urls {
        unique_urls := []string{}
        unique_urls = append(unique_urls, url_d)
    }*/
    for i := 0; i < NUM_HOPS; i++ {
        // Crawl processed concurrently       
        Site := make([]Sites, len(all_urls))
        ctx, _ := context.WithCancel(context.Background())
        for j,url_u := range all_urls {
            _, err := url.ParseRequestURI(url_u)
            if err != nil {
                fmt.Println("Incorrect url prasing" + url_u)
            }  else {
                wg.Add(1)
                sem  <- 1
                Site[j].url = url_u
                go func() {
                   crawlHelper(ctx,&wg,&Site[j],links,image,failed,j,html_files)
                   <-sem
                }()
                time.Sleep(100*time.Millisecond) 
                
                if j%1000 == 0 {
                    fmt.Println(j)
                }
            } 
        }
        fmt.Println("SLEEPING")
        time.Sleep(30*time.Second) 
        fmt.Println("STARTING NEW CRAWL")
        all_urls = unique(new_urls)
        new_urls = nil
        fmt.Println(len(all_urls))
        if len(all_urls) == 0 {
            _, err := nlonger.WriteString("no more unique urls\n")
            if err != nil {
                fmt.Println("ERROR: " + err.Error())
                return 
            }
            break 
        }
      
        _, err = scraped.WriteString("scraped this url\n")
        if err != nil {
            fmt.Println("ERROR: " + err.Error())
            return 
        }
        crawled_urls = nil
        fmt.Println(num_scraped)
        
    }
    wg.Wait()
    time.Sleep(200*time.Second) 
    fmt.Println("WAITING")
    err = f.Close()
    if err != nil {
        fmt.Println("Failed to close file")
       ///log.Fatal(err)
    }   

    err = nlonger.Close()
    if err != nil {
        fmt.Println("Failed to close file")
       ///log.Fatal(err)
    }  

    err = scraped.Close()
    if err != nil {
        fmt.Println("Failed to close file")
       ///log.Fatal(err)
    } 
    err = links.Close()
    if err != nil {
        fmt.Println("Failed to close file")
       ///log.Fatal(err)
    }   
    err = failed.Close()
    if err != nil {
        fmt.Println("Failed to close file")
       ///log.Fatal(err)
    }   
    err = image.Close()
    if err != nil {
        fmt.Println("Failed to close file")
       ///log.Fatal(err)
    }   
	
        err = html_files.Close()
        if err != nil {
            fmt.Println("Failed to close file")
           ///log.Fatal(err)
        }   
    fmt.Printf("\n\nScraped succesfully\n\n")
}
