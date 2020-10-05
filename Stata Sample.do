*****************************************************
* Shoppertrack Data          						*
* Author: Zhen Yuan  								*
* Date: 08/12/2020									*
* Last edit: 10/1/2020  							*
* Purpose: Comapre 19 and 20 traffic                *
*****************************************************

*** STEP 1:
***** Generate dataset for Chain Category

clear all
import delimited "ShopperTrak\crosswalk\chain_categories_20200529.csv", clear
keep chain_id category_id

*** Make Chain_id unique identifiers 
sort chain_id
quietly by category_id chain_id:  gen dup = cond(_N==1,0,_n)
drop if dup > 1
drop dup

save "shoppertrack\chain_cat.dta", replace

*******************************////////////////*********************************

*** STEP 2:
***** Generate dataset for Site state_prov

import delimited "ShopperTrak\crosswalk\site_state_prov_20200529.csv", varnames(1) clear 
keep site_id chain_id 
duplicates drop
drop if missing(chain_id) 
*** Check and drop non numeric observations / Also drop sites not belong to chain
gen byte notnumeric = real(chain_id)==.
tab notnumeric
list chain_id if notnumeric==1
drop if notnumeric==1
drop notnumeric

save "shoppertrack\store.dta", replace

*******************************////////////////*********************************

*** STEP 3:
***** Merge with Traffic Data
clear all
import delimited "shoppertrack\sites.csv", clear
keep site_id state_prov
duplicates drop site_id, force
destring site_id, replace force
drop if missing(site_id) 
save "sites.dta", replace

import delimited "shoppertrack\traffic.csv", clear
merge m:1 site_id using "shoppertrack\sites.dta"
keep if _merge == 3
drop _merge
merge m:1 site_id using "shoppertrack\store.dta"
keep if _merge == 3
drop _merge
merge m:1 chain_id using "shoppertrack\chain_cat.dta"
keep if _merge == 3
drop _merge

save "shoppertrack\final_traffic.dta", replace

*******************************////////////////*********************************

*** STEP 4: Regression

*** Step 4.1
*** Run regression on the year-to-year difference in traffic 

use "final_traffic.dta", clear

*** Tables

{
	reghdfe diff policy daily_cases daily_deaths cases_per_100000 deaths_per_100000, absorb(site_id) 
	outreg2 using "tables\diff_all_categories.tex",/*
	*/append addtext(site_id FE,Yes, Category,`cat')
	di "`cat'"      
	foreach cat in "Candy & CardGift" "Home Furnishings" "Housewares & Kitchenwares" "Office Products"/*
	*/ "Dept store" "Sporting Goods" "Toy & Hobby" "General Merchandise"  "Pets" /*
	*/ "Electronics & Wireless" "Optical & Sunglass" "Shoes" "Children's Apparel" "Women's Apparel" /*
	*/ "Family Apparel" "Jewelry" "Accessories" "Men's Apparel" "Cosmetics & Sundries"/*
	*/ "Luxury"{       
		reghdfe diff policy daily_cases daily_deaths cases_per_100000 deaths_per_100000/*
		*/ if category_name == "`cat'", absorb(site_id) 
 		outreg2 using "tables\diff_all_categories.tex",/*
		*/append addtext(site_id FE,Yes, Category,`cat')
		di "`cat'"
		}  
}



*** Graphs


{
	local mcode 0
	reghdfe diff policy daily_cases daily_deaths  cases_per_100000 deaths_per_100000, absorb(site_id)  
	estimates store subgraph_`mcode'

	foreach cat in  "Candy & CardGift" "Home Furnishings" "Housewares & Kitchenwares" "Office Products"/*
	*/ "Dept store" "Sporting Goods" "Toy & Hobby" "General Merchandise"  "Pets" /*
	*/ "Electronics & Wireless" "Optical & Sunglass" "Shoes" "Children's Apparel" "Women's Apparel" /*
	*/ "Family Apparel" "Jewelry" "Accessories" "Men's Apparel" "Cosmetics & Sundries"/*
	*/ "Luxury"{
	    local mcode = `mcode' + 1
		reghdfe diff policy daily_cases daily_deaths  cases_per_100000 /*
		*/deaths_per_100000 if category_name == "`cat'", absorb(site_id) 
		estimates store subgraph_`mcode'

	}
	coefplot (subgraph_0, label ("All"))(subgraph_1, label ("Candy & CardGift")) /*
	*/(subgraph_2 , label ("Home Furnishings")) (subgraph_3 , label ("Housewares")) /*
	*/(subgraph_4 , label ("Office Products"))(subgraph_5, label ( "Dept store"))/*
	*/(subgraph_6 , label ( "Sporting Goods")) (subgraph_7 , label (  "Toy & Hobby"))/*
	*/(subgraph_8, label ( "General Merchandise")) (subgraph_9 , label ("Pets"))/*
	*/(subgraph_10, label ( "Electronics & Wireless")) (subgraph_11 , label ( "Optical & Sunglass"))/*
	*/(subgraph_12 , label ( "Shoes")) (subgraph_13, label ( "Children's Apparel" )) /*
	*/(subgraph_14 , label ("Women's Apparel"))(subgraph_15 , label ("Family Apparel"))/* 
	*/(subgraph_16, label ( "Jewelry" )) (subgraph_17 , label ("Accessories"))/*
	*/(subgraph_18 , label ("Men's Apparel")) (subgraph_19 , label ("Cosmetics & Sundries")) /*
	*/(subgraph_20, label ("Luxury")) , coeflabels(policy = "Stay-at-Home Policy") /*
	*/ drop(_cons daily_cases daily_deaths cases_per_100000 deaths_per_100000)  /*
	*/vertical  legend(col(3) size(tiny) ) graphregion(color(white)) bgcolor(white) xlabels(, nolabels) /*
	*/xtitle("Stay-at-Home Policy") ytitle("Difference in Traffic") /*
	*/title("Effect of Policy on Traffic per Operating Hours by Categories", span size(Small)) 
	graph export  "graphs\coefplots\coefplot_all_categories.pdf",replace
}






*** Step 4
*** Regression on policy with day of the week effect

use "final_traffic.dta", clear


gen Monday = 1 if day_of_week == 0
replace Monday = 0 if day_of_week != 0  

gen Tuesday = 1 if day_of_week == 1
replace Tuesday = 0 if day_of_week != 1 

gen Wednesday = 1 if day_of_week == 2
replace Wednesday = 0 if day_of_week != 2 

gen Thursday = 1 if day_of_week == 3
replace Thursday = 0 if day_of_week != 3 

gen Friday = 1 if day_of_week == 4
replace Friday = 0 if day_of_week != 4 

gen Saturday = 1 if day_of_week == 5
replace Saturday = 0 if day_of_week != 5 

gen Sunday = 1 if day_of_week == 6
replace Sunday = 0 if day_of_week != 6

***** Generate week of day * policy
gen Monday_policy = 1 if Monday*policy == 1
replace Monday_policy = 0 if Monday*policy != 1

gen Tuesday_policy = 1 if Tuesday*policy == 1
replace Tuesday_policy = 0 if Tuesday*policy != 1

gen Wednesday_policy = 1 if Wednesday*policy == 1
replace Wednesday_policy = 0 if Wednesday*policy != 1

gen Thursday_policy = 1 if Thursday*policy == 1
replace Thursday_policy = 0 if Thursday*policy != 1

gen Friday_policy = 1 if Friday*policy == 1
replace Friday_policy = 0 if Friday*policy != 1

gen Saturday_policy = 1 if Saturday*policy == 1
replace Saturday_policy = 0 if Saturday*policy != 1 

gen Sunday_policy = 1 if Sunday*policy == 1
replace Sunday_policy = 0 if Sunday*policy != 1



*** Tables
{  
	reghdfe diff policy daily_cases daily_deaths cases_per_100000 deaths_per_100000 /*
	*/Tuesday Wednesday Thursday Friday Saturday Sunday Tuesday_policy Wednesday_policy /*
	*/Thursday_policy Friday_policy Saturday_policy Sunday_policy, absorb(site_id) 
	outreg2 using "D:\wharton_ra\shoppertrack\final\graphs&tables\tables\day_of_week_all_categories.tex",/*
	*/append addtext(site_id FE,Yes, Category,`cat')
	di "`cat'"    
	foreach cat in "Candy & CardGift" "Home Furnishings" "Housewares & Kitchenwares" "Office Products"/*
	*/ "Dept store" "Sporting Goods" "Toy & Hobby" "General Merchandise"  "Pets" /*
	*/ "Electronics & Wireless" "Optical & Sunglass" "Shoes" "Children's Apparel" "Women's Apparel" /*
	*/ "Family Apparel" "Jewelry" "Accessories" "Men's Apparel" "Cosmetics & Sundries"/*
	*/ "Luxury"{       
		reghdfe diff policy daily_cases daily_deaths  cases_per_100000 deaths_per_100000/*
		*/Tuesday Wednesday Thursday Friday Saturday Sunday Tuesday_policy /*
		*/Wednesday_policy Thursday_policy Friday_policy/*
		*/ Saturday_policy Sunday_policy if category_name == "`cat'", absorb(site_id) 
		outreg2 using "D:\wharton_ra\shoppertrack\final\graphs&tables\tables\day_of_week_all_categories.tex",/*
		*/append addtext(site_id FE, Yes, Category,`cat')
		di "`cat'"
		}  
}








*** Step 4
*** Generate 10-day Average Traffic Trendline 
use "final_traffic.dta", replace
drop transaction_date_19
generate date = date(transaction_date_20, "YMD")
format %td date
save "dist_trendline.dta", replace

bysort district category_name date: egen cat_enters_20 = mean(hourly_enters_20) 
bysort district category_name date: egen cat_enters_19 = mean(hourly_enters_19) 
quietly bysort district category_name date: gen dup = cond(_N==1,0,_n)
drop if dup > 1
keep district category_id category_name segment_id segment_name date cat_enters_20 cat_enters_19
gen month=month(date)
gen day = day(date)
gen year = year(date)
gen group = int(day/10)
replace group = 2  if group==3
bys district category_name month group: egen mean_20 = mean(cat_enters_20)
bys district category_name month group: egen mean_19 = mean(cat_enters_19)
sort district category_name month group
quietly by district category_name month group:  gen dup = cond(_N==1,0,_n)
drop if dup>1
drop dup
replace date = mdy(month,5,year) if group == 0
replace date = mdy(month,15,year) if group == 1
replace date = mdy(month,25,year) if group == 2
format %td date
save "dist_trendline.dta", replace

clear all
use "dist_trendline.dta"
 
*** Trendline for districts

foreach dist in "New_England" "Mid_Atlantic" "West_North_Central" "South_Atlantic"/*
*/ "East_South_Central" "West_South_Central" "Mountain" "Pacific"{

	foreach cat in  "Candy & CardGift" "Home Furnishings" "Housewares & Kitchenwares" "Office Products"/*
	*/ "Dept store" "Sporting Goods" "Toy & Hobby" "General Merchandise"  "Pets" /*
	*/ "Electronics & Wireless" "Optical & Sunglass" "Shoes" "Children's Apparel" "Women's Apparel" /*
	*/ "Family Apparel" "Jewelry" "Accessories" "Men's Apparel" "Cosmetics & Sundries"/*
	*/ "Luxury"{ 
		clear 
		use "dist_trendline.dta" 
		keep if category_name == "`cat'" & district == "`dist'"
		tsset date
		tsline mean_20 mean_19, graphregion(color(white)) bgcolor(white) /*
		*/title("Average Number of Customers Entering a Store per Operating Hour", span size(Small))/*
		*/ytitle("Number of Enters")  xlabel(, format(%tdM)) legend(label(1 "2020 store traffic") /* 
		*/label(2 "2019 store traffic") col(3) size(small)) 
		graph export  "trend_`dist'_`cat'.pdf",replace
		
	}  
}
	

*** Trendline for categories


foreach cat in  "Candy & CardGift" "Home Furnishings" "Housewares & Kitchenwares" "Office Products"/*
*/ "Dept store" "Sporting Goods" "Toy & Hobby" "General Merchandise"  "Pets" /*
*/ "Electronics & Wireless" "Optical & Sunglass" "Shoes" "Children's Apparel" "Women's Apparel" /*
*/ "Family Apparel" "Jewelry" "Accessories" "Men's Apparel" "Cosmetics & Sundries"/*
*/ "Luxury"{ 
	clear 
	use "D:\wharton_ra\shoppertrack\trendline.dta" 
	keep if category_name == "`cat'"
	tsset date
	tsline mean_20 mean_19, graphregion(color(white)) bgcolor(white) /*
	*/title("Average Number of Customers Entering a Store per Operating Hour", span size(Small)) /*
	*/ytitle("Number of Enters")  xlabel(, format(%tdM)) legend(label(1 "2020 store traffic") /*
	*/label(2 "2019 store traffic") col(3) size(small) ) 
	graph export  "D:\wharton_ra\shoppertrack\reg2_tables\10_day_trend\trend_`cat'.pdf",replace
		
	}  

	




