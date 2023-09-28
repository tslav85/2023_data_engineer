-- public.trascheev_project_ssd definition

-- Drop table

-- DROP TABLE public.trascheev_project_ssd;

CREATE TABLE public.trascheev_project_ssd (
	usercode varchar(255) NOT NULL,
	sensorcode varchar(255) NOT NULL,
	"time" timestamp NOT NULL,
	status int4 NULL
)
WITH (
	appendonly=true,
	orientation=column
)
DISTRIBUTED RANDOMLY;