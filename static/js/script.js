import { createUseStyles } from 'jss';

const useStyles = createUseStyles({
  activeLink: {
    color: 'red',
  },
});

function MyComponent() {
  const classes = useStyles();

  return (
    <div>
      <a href="#" className={classes.activeLink}>Active Link</a>
    </div>
  );
}
