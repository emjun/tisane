# Tisane
# Barr et al. 2012: 'Keep it Maximal'

# Install packages
install.packages('multicore')
install.packages("simgen-master.zip")

# Load package
library(simgen)

# Define randParams (from simgen master branch)
randParams <- function(plist, nmc=1, firstseed=NULL) {
  if (!is.null(firstseed)) {
    set.seed(firstseed)
  } else {}
  if (is.vector(plist)) {
    plist <- as.list(plist)
  } else {}
  if (is.null(names(plist))) {
    names(plist) <- paste("V", 1:length(plist), sep="")
  } else {}
  ff <- lapply(names(plist), function(nx) {
    x <- plist[[nx]]
    if (is.list(x)) {
      rge <- x[[sample(1:length(x),1)]] # randomly choose ranges with eq prob
    } else {
      rge <- x
    }
    if (length(rge)==1) {
      res <- rep(rge, nmc)
    } else {
      res <- runif(nmc, rge[1], rge[2])
    }
  })
  matrix(unlist(ff), nrow=nmc, dimnames=list(NULL, names(plist)))
}

genParamRanges <- function() {
  list(
    int=c(-3,3),       # range of intercept value, continuous simulations
    eff=.8,            # set to 0 to test Type I error rate
    err=c(0,3),         # range for error variance
    miss=c(0,.05),     # proportion of missing data
    pMin=0,                # lower bound on condition/cluster-level rate of  missing data
    pMax=0.8,              # lower bound on condition/cluster-level rate of  missing data
    t00=c(0, 3),         # tau_00 is the subject variance for the intercept
    t11=c(0, 3),         # tau_11 is the subject variance for the slope
    rsub=c(-.8, .8), # range of the by-subject intercept/slope correlation
    w00=c(0, 3),         # by-item intercept variance
    w11=c(0, 3),         # by-item slope variance
    ritm=c(-.8, .8) # by-item intercept/slope correlation
  )
}

mkSeeds <- function(nmc=1000, firstseed=NULL) {
  randSeed <- function(n=1) {
    # seeds must all be unique!
    seeds <- c()
    nremaining <- n
    nTries <- 1
    nMaxTries <- 1000
    while (nremaining & (nTries < nMaxTries)) {
      seeds <- unique(c(seeds, round((.Machine$integer.max-1)*(runif(nremaining, min=0, max=1)),0)))
      nremaining <- n-length(seeds)
      nTries <- nTries + 1
    }
    if (nTries == nMaxTries) {
      stop("couldn't create enough unique random seeds after 1000 tries!")
    } else {}
    return(seeds)
  }
  if (!is.null(firstseed)) {
    set.seed(firstseed)
  } else {}
  randSeed(nmc)    
}


# Generate data
nmc <- 10
pmx <- cbind(randParams(genParamRanges(), nmc, 1001), seed=mkSeeds(nmc, 1001))

# wsbi: whether the design is between-items (TRUE) or within-items (FALSE)
# WSBI: Between-items
x1.df <- mkDf(nsubj=24, nitem=24, mcr.params=pmx[1,], wsbi=FALSE)

# WSBI: Within-items
x2.df <- mkDf(nsubj=24, nitem=24, mcr.params=pmx[1,], wsbi=TRUE)

# number of Monte Carlo runs (nexp)
# set to small value for testing purposes
# NOTE: change this to 100000 for full replication
pmx <- createParamMx(nexp=50, h0=TRUE)

# ----------- Type I Error (H0 true) ------------
pmx[,"eff"] <- 0

# lmer models, maximal
mcRun("fitlmer", mcr.outfile="fitlmerRS.h0.wsbi.12.csv",
      mcr.xdatFnc="mkDf", mcr.varying=pmx, nitem=12, wsbi=TRUE)
mcRun("fitlmer", mcr.outfile="fitlmerRS.h0.wsbi.24.csv",
      mcr.xdatFnc="mkDf", mcr.varying=pmx, nitem=24, wsbi=TRUE)
mcRun("fitlmer", mcr.outfile="fitlmerRS.h0.wswi.12.csv",
      mcr.xdatFnc="mkDf", mcr.varying=pmx, nitem=12, wsbi=FALSE)
mcRun("fitlmer", mcr.outfile="fitlmerRS.h0.wswi.24.csv",
      mcr.xdatFnc="mkDf", mcr.varying=pmx, nitem=24, wsbi=FALSE)
