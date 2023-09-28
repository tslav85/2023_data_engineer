-- public.trascheev_project_sil definition

-- Drop table

-- DROP TABLE public.trascheev_project_sil;

CREATE TABLE public.trascheev_project_sil (
	usercode varchar(255) NOT NULL,
	sensorcode varchar(255) NOT NULL,
	"time" timestamp NOT NULL,
	lighting float8 NULL,
	light_temp varchar(255) NULL
)
WITH (
	appendonly=true,
	orientation=column
)
DISTRIBUTED RANDOMLY;