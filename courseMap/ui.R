#Title: ui.R of Shiny App Course Map System
#Author: Dillan Smith
#Date 4/4/2017
#All rights reserved
require(shiny)
require(visNetwork)
require(igraph)
#full page
navbarPage("Course Map", id="nav",
           
           #tutorial tab with embedded pdf
           tabPanel("Tutorial",
                    
                    tabPanel("Reference", 
                             tags$iframe(style="height:1000px; width:100%; scrolling=yes", 
                                         src="map.pdf"))
           ),
           #second tab with graph 
           tabPanel("Interactive Map",
                    sidebarLayout(
                      sidebarPanel(
                        #checkboxInput("hierarchy", label = "Hierarchichal Layout", value = FALSE),
                        checkboxInput("smooth", label = "Smooth Edges", value = TRUE),
                        textOutput("nodes_id"),
                        textOutput('nodes_title'),
                        textOutput("nodes_summary"),
                        actionButton("getNodes", "Nodes")
                        
                        
                      ),
                      #the graph
                      mainPanel(
                        visNetworkOutput("network", height = "1000px")
                      )
                    )
                    
                    
                    
           ),
           #final tab with the database in it
           tabPanel("Data Explorer",
                    fluidRow(
                      DT::dataTableOutput("table")
                    )
                    
                    
                    
           )
           
           
           
)