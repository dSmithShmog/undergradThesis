#Title: server.R portion of Shiny App Course Map system
#Author: Dillan Smith
#Date: 4/4/2017
#All rights reserved

require(visNetwork)
require(shiny)
require(igraph)
function(input, output){
  #import nodes and edges file create in textMiner
  nodes <- read.table("nodes.tsv", sep = "\t", header=T, as.is=T)
  links <- read.table("edges.tsv", sep = "\t", header=T, as.is=T)
  db <- read.delim("database.tsv", sep = "\t", header=T, as.is = T)
  
  #create interactive graph
  output$network <- renderVisNetwork({
    
    
    nodes$shape <- "dot"  
    nodes$shadow <- TRUE # Nodes will drop shadow
    nodes$title <- nodes$title # Text on click
    nodes$label <- nodes$id # Node label
    nodes$size <- 12 # Node size
    nodes$borderWidth <- 2 # Node border width
    nodes$color.background <- c("slategrey", "tomato", "gold", "blueviolet", "burlywood", "burlywood4",
                                "black", "coral2", "chocolate", "cadetblue1", "brown", "aquamarine1", 
                                "deepskyblue4", "deeppink4", "darkslategray4", "darkseagreen", "darksalmon", 
                                "deeppink", "darkorchid4", "khaki1", "hotpink3", "limegreen", "maroon4", "orangered1",
                                "orange1", "seagreen", "royalblue", "royalblue4", "red", "red4", "purple", 
                                "slateblue4", "springgreen", "springgreen4", "peru")[nodes$deptNum]
    nodes$color.border <- "black"
    nodes$color.highlight.background <- "orange"
    nodes$color.highlight.border <- "darkred"
    links$arrows <- "to"
    visNetwork(nodes,links)%>%
      visOptions(selectedBy = "dept", nodesIdSelection = TRUE)%>%
      #get the id of the node being clicked on when clicked
      visEvents(select = "function(nodes) {
                Shiny.onInputChange('current_node_id', nodes.nodes);
                ;}")%>%
      #visPhysics(stabilization = FALSE)
      #visIgraphLayout()
      #prevent users from dragging nodes
      visInteraction(dragNodes = FALSE)%>%
      #visEdges(smooth = FALSE)%>%
      #option based on check box in UI
      visIgraphLayout(smooth = input$smooth)#%>%
    #visLayout(hierarchical = input$hierarchy)
    #visLayout(randomSeed = 123)
    
})
  
  #gets id of node that clicked on
  observeEvent(input$current_node_id, {
    visNetworkProxy("network") %>%
      visGetNodes()
    visFocus(visNetworkProxy("network"), input$current_node_id, scale = 1,  offset =  list(x = 0, y = -150))
  })
  
  #the database created the tsv file from the textMiner
  output$table <- DT::renderDataTable(db)
  
  #Output summary of clicked on node
  output$nodes_summary <- renderText( {
    
    paste("Summary:",db[match(input$current_node_id, nodes[,"id"])[1], "summary"])
    
  })
  
  #output title of clicked on node
  output$nodes_title <- renderText({
    paste("Title: ",db[match(input$current_node_id, nodes[, "id"])[1], "title"])
  })
  
  #output id of clicked on node
  output$nodes_id <- renderText({
    paste("ID:",db[match(input$current_node_id, nodes[, "id"])[1], "id"])
  })
  
  #output$nodes_name <- renderText(paste(db[match(input$current_node_id, nodes[, "id"])[1], "id"],
  #db[match(input$current_node_id, nodes[, "id"])[1], "title"]
  #))
  
  
  
  
  
  
  
  }