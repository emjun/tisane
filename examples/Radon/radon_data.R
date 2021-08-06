# Example and data from Gelman and Hill
# Data are at http://www.stat.columbia.edu/~gelman/arm/examples/radon
# To author this script, I have taken bits and pieces from example scripts in the book/supplementary material

# Import libraries
library(lme4)

# Read in data
srrs2 <- read.table ("./examples/Radon/srrs2.dat", header=T, sep=",")
mn <- srrs2$state=="MN"
radon <- srrs2$activity[mn]
log.radon <- log (ifelse (radon==0, .1, radon))
floor <- srrs2$floor[mn]       # 0 for basement, 1 for first floor
n <- length(radon)
y <- log.radon
x <- floor

# Get county index variable
county.name <- as.vector(srrs2$county[mn])
uniq <- unique(county.name)
J <- length(uniq)
county <- rep (NA, J)
for (i in 1:J){
  county[county.name==uniq[i]] <- i
}

# Get the county-level predictor
srrs2.fips <- srrs2$stfips*1000 + srrs2$cntyfips
cty <- read.table ("./examples/Radon/cty.dat", header=T, sep=",")
usa.fips <- 1000*cty[,"stfips"] + cty[,"ctfips"]
usa.rows <- match (unique(srrs2.fips[mn]), usa.fips)
uranium <- cty[usa.rows,"Uppm"]
u <- log(uranium)

# Varying-intercept model w/ group-level predictors
u.full <- u[county]

## Run models from Chapter 13 to make sure that the data is as expected. 
# Floor + County
M3 <- lmer(y ~ x + (1 + x | county))
display (M3)

# Floor, County uranium, County
M4 <- lmer (y ~ x + u.full + x:u.full + (1 + x | county))
display (M4)
coef (M4)
fixef (M4)
ranef (M4)

# Output data file
df = data.frame(y, x, county, u.full)
write.csv(df, "./examples/Radon/radon_data_combined.csv")
# After exporting the data, rename the index column "household" 