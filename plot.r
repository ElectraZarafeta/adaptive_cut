plotLinkCommDend <- function(x, col=TRUE, pal = brewer.pal(9,"Set1"), height=x$pdmax, right = FALSE, labels=FALSE, plotcut=TRUE, droptrivial = TRUE, leaflab = "none", verbose = TRUE, ...)
	# x is a "linkcomm" object.
	{
	dd <- as.dendrogram(x$hclust)
	if(col){
		cl <- unlist(x$clusters)
		crf <- colorRampPalette(pal,bias=1)
		cols <- crf(length(x$clusters))
		cols <- sample(cols,length(x$clusters),replace=FALSE)
		numnodes <- nrow(x$hclust$merge) + length(which(x$hclust$merge[,1]<0)) + length(which(x$hclust$merge[,2]<0))
		dd <- dendrapply(dd, .COL, height=height, clusters=cl, cols=cols, labels=labels, numnodes = numnodes, droptrivial = droptrivial, verbose = verbose)
		cat("\n")
		assign("i",0,environment(.COL))
		assign("memb",0,environment(.COL))
		assign("first",0,environment(.COL))
		assign("left",0,environment(.COL))
		}
	if(right){
		dd <- rev(dd)
		}
	plot(dd,ylab="Height", leaflab = leaflab, ...)
	if(plotcut){
		abline(h=height,col='red',lty=2,lwd=2)
		}
	#ll <- sapply(x$clusters,length)
	#maxnodes <- length(unique(x$nodeclusters[x$nodeclusters[,2]%in%which(ll==max(ll)),1]))
	summ <- paste("# clusters = ",length(x$clusters),"\nLargest cluster = ",x$clustsizes[1]," nodes")
	mtext(summ, line = -28)
	}