public class HelloWorld {

	public static void main(String[] arg){
		System.out.println("Hello world");
	}
	
	public static void variadic_main(String ... arg){
		System.out.println("Hello world");
	}

}

abstract class Animal {

	public abstract void move();

}

public class Dog extends Animal {

	private int position = 0;

    public static Dog create() {
		return new Dog()
	}

    public void bark(String sound, int repeat) {
		for (int i = 0; i < repeat; i++) {
			System.out.println(sound);
		}
	}

	@override
	public void move() {
		position++;
	}

}
