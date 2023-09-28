-- public.trascheev_project_sol definition

-- Drop table

-- DROP TABLE public.trascheev_project_sol;

CREATE TABLE public.trascheev_project_sol (
	usercode varchar(255) NOT NULL,
	sensorcode varchar(255) NOT NULL,
	"time" timestamp NOT NULL,
	lighting float8 NULL
)
WITH (
	appendonly=true,
	orientation=column
)
DISTRIBUTED RANDOMLY;