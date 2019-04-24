library(tidyverse)

spore <- fread("app/static/songs_with_recommendations_and_2d_proj_60k.csv")
quant_spore = spore[,c("danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo")]
hist(spore$tempo)
par(mfrow = c(2,1))

ggplot(spore) + 
  geom_histogram(aes(x = loudness), binwidth = .5, colour = "#fdbb84", fill = "#fdbb84") + 
  theme_classic() + 
  xlab("Loudness") + 
  ylab("Frequency") +
  coord_flip()

ggplot(spore) + 
  geom_histogram(aes(x = tempo), binwidth = .5, colour = "#99d8c9", fill = "#99d8c9") + 
  theme_classic() 

quant_spore$tempo <- spore$tempo/max(spore$tempo)
quant_spore$loudness <- spore$loudness/min(spore$loudness)
