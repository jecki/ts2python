// Just for testing

interface CalendarJSON {
	  date: string;
	  fiscal: {
		month: MonthNumbers;
		quarter:
		  | { name: 'Q1'; value: 1 }
		  | { name: 'Q2'; value: 2 }
		  | { name: 'Q3'; value: 3 }
		  | { name:; 'Q4'; value: 4 };
		week: WeekNumbers;
		year: CommonYears;
	  };
	  gregorian: {
		day_of_week:
		  | { name: 'Monday'; value: 0 }
		  | { name: 'Tuesday'; value: 1 }
		  | { name: 'Wednesday'; value: 2 }
		  | { name: 'Thursday'; value: 3 }
		  | { name: 'Friday'; value: 4 }
		  | { name: 'Saturday'; value: 5 }
		  | { name: 'Sunday'; value: 6 };
		month: MonthNumbers;
		quarter: QuarterNumbers;
		week: WeekNumbers;
		year: CommonYears;
	  };
	  id: string;
	}