public class HelloWorld {

	public static void main(String[] arg){
		System.out.println("Hello world");
	}
	
	public static void variadic_main(String ... arg){
		System.out.println("Hello world");
	}

}

/**
 * Abstract representation of an animal
 */
abstract class Animal {

	/**
	 * Move the animal
	 */
	public abstract void move();

}

public class Dog extends Animal {

	private int position = 0;

	/**
	 * @return a new dog
	 */
    public static Dog create() {
		return new Dog()
	}

	/**
	 * Bark
	 * @param sound: sound of the dog
	 * @param repeat: number of repeat
	 */
    public void bark(String sound, int repeat) {
		for (int i = 0; i < repeat; i++) {
			System.out.println(sound);
		}
	}

	/*
	 * Move the dog
	 */
	@override
	public void move() {
		position++;
	}

}
