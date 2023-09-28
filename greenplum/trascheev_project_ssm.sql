-- public.trascheev_project_ssm definition

-- Drop table

-- DROP TABLE public.trascheev_project_ssm;

CREATE TABLE public.trascheev_project_ssm (
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